"""The only way to call a model: registered operation, bounded attempts, validation, run record.

Nothing here writes workflow state, and no database transaction is open during inference.
"""

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

from app.ai.providers import Provider, ProviderError, current_provider
from app.shared.config import int_setting
from app.shared.contracts import AssistantOutput, DocumentExtractionOutput, InsightOutput, NextStep
from app.shared.db import connect
from app.shared.util import new_id, now_iso

logger = logging.getLogger("onboardiq.ai")


class AiUnavailable(Exception):
    """The model could not be reached. Callers must show a clear manual path."""

    def __init__(self, reason: str, run_id: str):
        super().__init__(reason)
        self.reason = reason
        self.run_id = run_id


class AiOutputRejected(Exception):
    """The model answered, but its output failed validation even after the single repair."""

    def __init__(self, reason: str, run_id: str):
        super().__init__(reason)
        self.reason = reason
        self.run_id = run_id


@dataclass(frozen=True)
class Operation:
    name: str
    prompt_version: int
    output_model: type[BaseModel]
    max_output_tokens: int
    timeout_seconds: int
    max_attempts: int = 2


OPERATIONS = {
    op.name: op
    for op in (
        Operation("assistant.answer", 1, AssistantOutput, 900, 20),
        Operation("document.extract", 1, DocumentExtractionOutput, 900, 30),
        Operation("insights.summarize", 1, InsightOutput, 700, 30),
        Operation("agent.next_step", 1, NextStep, 500, int_setting("MODEL_TIMEOUT_SECONDS", 30)),
    )
}


@dataclass
class RunResult:
    output: BaseModel
    run_id: str
    provider: str
    model: str
    is_stub: bool


def record_run(
    operation: str,
    prompt_version: int,
    provider: Provider,
    status: str,
    validation_result: str,
    *,
    user_id: str | None = None,
    hire_id: str | None = None,
    case_id: str | None = None,
    chunk_ids: tuple[str, ...] | list[str] = (),
    failure_reason: str | None = None,
    attempts: int = 0,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    latency_ms: int = 0,
    retrieval_ms: int | None = None,
) -> str:
    """Stores references and measurements only. Prompts and document text are never kept."""
    run_id = new_id("RUN")
    with connect() as connection:
        connection.execute(
            "INSERT INTO ai_runs (id, operation, prompt_version, provider, model, user_id, "
            "hire_id, case_id, chunk_ids_json, status, validation_result, failure_reason, "
            "attempts, input_tokens, output_tokens, latency_ms, retrieval_ms, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                run_id,
                operation,
                prompt_version,
                provider.name,
                provider.model,
                user_id,
                hire_id,
                case_id,
                json.dumps(list(chunk_ids)),
                status,
                validation_result,
                failure_reason,
                attempts,
                input_tokens,
                output_tokens,
                latency_ms,
                retrieval_ms,
                now_iso(),
            ),
        )
    logger.info(
        json.dumps(
            {
                "event": "ai_run",
                "run_id": run_id,
                "operation": operation,
                "status": status,
                "attempts": attempts,
                "latency_ms": latency_ms,
            }
        )
    )
    return run_id


def run_operation(
    name: str,
    messages: list[dict],
    *,
    user_id: str | None = None,
    hire_id: str | None = None,
    case_id: str | None = None,
    chunk_ids: tuple[str, ...] | list[str] = (),
    retrieval_ms: int | None = None,
    semantic_check: Callable[[BaseModel], str | None] | None = None,
    before_attempt: Callable[[], bool] | None = None,
) -> RunResult:
    """Call, parse, validate, then at most one repair. `before_attempt` enforces saved budgets."""
    operation = OPERATIONS[name]
    provider = current_provider()
    schema = operation.output_model.model_json_schema()
    conversation = [dict(message) for message in messages]
    started = time.monotonic()
    attempts = 0
    input_tokens = output_tokens = 0
    context = {
        "user_id": user_id,
        "hire_id": hire_id,
        "case_id": case_id,
        "chunk_ids": chunk_ids,
        "retrieval_ms": retrieval_ms,
    }

    def elapsed() -> int:
        return int((time.monotonic() - started) * 1000)

    failure = "NO_ATTEMPT"
    while attempts < operation.max_attempts:
        if before_attempt is not None and not before_attempt():
            failure = "BUDGET_EXHAUSTED"
            break
        attempts += 1
        try:
            reply = provider.generate(
                name,
                conversation,
                schema,
                operation.timeout_seconds,
                operation.max_output_tokens,
            )
        except ProviderError as exc:
            run_id = record_run(
                name,
                operation.prompt_version,
                provider,
                "UNAVAILABLE",
                "NOT_RUN",
                failure_reason=str(exc),
                attempts=attempts,
                latency_ms=elapsed(),
                **context,
            )
            raise AiUnavailable(str(exc), run_id) from exc
        input_tokens += reply.input_tokens or 0
        output_tokens += reply.output_tokens or 0
        try:
            output = operation.output_model.model_validate(json.loads(reply.text))
        except (json.JSONDecodeError, ValidationError):
            failure = "SCHEMA_INVALID"
        else:
            problem = semantic_check(output) if semantic_check else None
            if problem is None:
                run_id = record_run(
                    name,
                    operation.prompt_version,
                    provider,
                    "VALIDATED",
                    "PASSED_FIRST_TRY" if attempts == 1 else "PASSED_AFTER_REPAIR",
                    attempts=attempts,
                    input_tokens=input_tokens or None,
                    output_tokens=output_tokens or None,
                    latency_ms=elapsed(),
                    **context,
                )
                return RunResult(output, run_id, provider.name, provider.model, provider.is_stub)
            failure = problem
        conversation = [
            *conversation,
            {"role": "assistant", "content": reply.text[:4000]},
            {
                "role": "user",
                "content": f"That output was rejected ({failure}). Return corrected JSON only.",
            },
        ]
    run_id = record_run(
        name,
        operation.prompt_version,
        provider,
        "REJECTED_OUTPUT",
        failure,
        failure_reason=failure,
        attempts=attempts,
        input_tokens=input_tokens or None,
        output_tokens=output_tokens or None,
        latency_ms=elapsed(),
        **context,
    )
    raise AiOutputRejected(failure, run_id)
