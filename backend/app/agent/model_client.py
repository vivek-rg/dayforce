"""Track 6/P04: exactly two configured branches, same shared NextStep validation."""

from typing import Any

from app.shared.contracts import NextStep


def generate_next_step(messages: list[dict[str, str]], schema: dict[str, Any]) -> NextStep:
    # TODO P04: Ollama format or approved HTTPS response_format; key stays on server.
    # TODO P04: count SDK retries/timeouts; never silently fall back to cloud.
    raise NotImplementedError("P04: generate_next_step")
