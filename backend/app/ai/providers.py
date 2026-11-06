"""Model transports. Keys stay on the server, and there is never a silent fallback to another model.

`hosted` speaks the common OpenAI-compatible chat format, so Groq, Cerebras, Mistral and OpenRouter
are configuration rather than code. Only a transport actually exercised against a live model may
be described as validated: see docs/EVALUATION.md.
"""

import json
import time
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.ai.stub import StubProvider
from app.shared.config import live_setting, llm_model, llm_provider

MAX_RATE_LIMIT_WAIT_SECONDS = 20
RATE_LIMIT_WAITS = {"agent.next_step": 3}


def _retry_after(response) -> float | None:
    try:
        return max(0.0, float(response.headers.get("retry-after", "")))
    except (TypeError, ValueError):
        return None


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

    def _post(self, messages, timeout, max_tokens):
        try:
            return httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages,
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

    def generate(self, operation, messages, schema, timeout, max_tokens) -> Reply:
        guided = [dict(message) for message in messages]
        guided[0]["content"] += "\n\nReturn one JSON object matching this schema:\n" + json.dumps(
            schema
        )
        response = self._post(guided, timeout, max_tokens)
        # A rate-limited call ran no inference. Wait if the provider gives a short delay. The
        # background agent can wait longer than a person watching an assistant answer.
        waits = RATE_LIMIT_WAITS.get(operation, 1)
        while response.status_code == 429 and waits > 0:
            delay = _retry_after(response)
            if delay is None or delay > MAX_RATE_LIMIT_WAIT_SECONDS:
                break
            waits -= 1
            time.sleep(delay)
            response = self._post(guided, timeout, max_tokens)
        if response.status_code == 429:
            raise ProviderError("MODEL_RATE_LIMITED")
        if response.status_code == 400:
            # Groq reports malformed JSON from the model as a 400. That is bad output, not an
            # outage, so it goes through normal validation and the single repair attempt.
            try:
                error = response.json().get("error", {})
            except ValueError:
                error = {}
            if error.get("code") == "json_validate_failed":
                return Reply(text=str(error.get("failed_generation") or ""))
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
        return OllamaProvider(
            llm_model(), live_setting("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        )
    if kind == "hosted":
        base_url = live_setting("LLM_BASE_URL")
        api_key = live_setting("LLM_API_KEY")
        if not llm_model() or not api_key or not _approved_base_url(base_url):
            return DisabledProvider("MODEL_NOT_CONFIGURED")
        return HostedProvider(llm_model(), base_url, api_key)
    return DisabledProvider()
