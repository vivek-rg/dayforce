"""Model transports. Keys stay on the server, and there is never a silent fallback to another model.

`hosted` speaks the common OpenAI-compatible chat format, so Groq, Cerebras, Mistral and OpenRouter
are configuration rather than code. Only a transport actually exercised against a live model may
be described as validated: see docs/EVALUATION.md.
"""

import json
import os
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.ai.stub import StubProvider
from app.shared.config import llm_model, llm_provider


class ProviderError(Exception):
    """Sanitized failure: holds a short reason, never a raw provider body or header."""


@dataclass
class Reply:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class Provider(Protocol):
    name: str
    model: str
    is_stub: bool
    is_local: bool

    def generate(
        self, operation: str, messages: list[dict], schema: dict, timeout: float, max_tokens: int
    ) -> Reply: ...


class OllamaProvider:
    name = "ollama"
    is_stub = False
    is_local = True

    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, operation, messages, schema, timeout, max_tokens) -> Reply:
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "format": schema,
                    "options": {"num_predict": max_tokens, "temperature": 0},
                },
                timeout=timeout,
                follow_redirects=False,
            )
        except httpx.TimeoutException as exc:
            raise ProviderError("MODEL_TIMEOUT") from exc
        except httpx.HTTPError as exc:
            raise ProviderError("MODEL_UNREACHABLE") from exc
        if response.status_code != 200:
            raise ProviderError(f"MODEL_HTTP_{response.status_code}")
        body = response.json()
        return Reply(
            text=body.get("message", {}).get("content", ""),
            input_tokens=body.get("prompt_eval_count"),
            output_tokens=body.get("eval_count"),
        )


class HostedProvider:
    name = "hosted"
    is_stub = False
    is_local = False

    def __init__(self, model: str, base_url: str, api_key: str):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def generate(self, operation, messages, schema, timeout, max_tokens) -> Reply:
        guided = [dict(message) for message in messages]
        guided[0]["content"] += "\n\nReturn one JSON object matching this schema:\n" + json.dumps(
            schema
        )
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": guided,
                    "temperature": 0,
                    "max_tokens": max_tokens,
                    "response_format": {"type": "json_object"},
                },
                timeout=timeout,
                follow_redirects=False,
            )
        except httpx.TimeoutException as exc:
            raise ProviderError("MODEL_TIMEOUT") from exc
        except httpx.HTTPError as exc:
            raise ProviderError("MODEL_UNREACHABLE") from exc
        if response.status_code == 429:
            raise ProviderError("MODEL_RATE_LIMITED")
        if response.status_code != 200:
            raise ProviderError(f"MODEL_HTTP_{response.status_code}")
        body = response.json()
        usage = body.get("usage", {})
        return Reply(
            text=body["choices"][0]["message"]["content"] or "",
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )


class DisabledProvider:
    name = "none"
    model = "none"
    is_stub = False
    is_local = True

    def __init__(self, reason: str = "AI_NOT_CONFIGURED"):
        self.reason = reason

    def generate(self, operation, messages, schema, timeout, max_tokens) -> Reply:
        raise ProviderError(self.reason)


_override: Provider | None = None


def set_provider_for_tests(provider: Provider | None) -> None:
    global _override
    _override = provider


def _approved_base_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith(
        ("http://127.0.0.1", "http://localhost")
    )


def current_provider() -> Provider:
    if _override is not None:
        return _override
    kind = llm_provider()
    if kind == "stub":
        return StubProvider()
    if kind == "ollama":
        if not llm_model():
            return DisabledProvider("MODEL_NOT_CONFIGURED")
        return OllamaProvider(llm_model(), os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    if kind == "hosted":
        base_url = os.getenv("LLM_BASE_URL", "")
        api_key = os.getenv("LLM_API_KEY", "")
        if not llm_model() or not api_key or not _approved_base_url(base_url):
            return DisabledProvider("MODEL_NOT_CONFIGURED")
        return HostedProvider(llm_model(), base_url, api_key)
    return DisabledProvider()
