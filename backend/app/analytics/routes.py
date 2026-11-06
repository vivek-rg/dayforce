import json

from fastapi import APIRouter, Depends

from app.ai.harness import AiOutputRejected, AiUnavailable
from app.ai.providers import current_provider
from app.analytics import service
from app.auth.permissions import require
from app.auth.service import require_user
from app.shared.contracts import (
    AiHealth,
    AiRun,
    AiRunList,
    AuditEvent,
    AuditEventList,
    InsightMetrics,
    InsightSummary,
    Metrics,
    Overview,
    User,
)
from app.shared.db import connect
from app.shared.errors import fail, not_found

router = APIRouter(tags=["analytics"])


def _to_run(row) -> AiRun:
    return AiRun(
        id=row["id"],
        operation=row["operation"],
        prompt_version=row["prompt_version"],
        provider=row["provider"],
        model=row["model"],
        user_id=row["user_id"],
        hire_id=row["hire_id"],
        case_id=row["case_id"],
        chunk_ids=json.loads(row["chunk_ids_json"]),
        status=row["status"],
        validation_result=row["validation_result"],
        failure_reason=row["failure_reason"],
        attempts=row["attempts"],
        input_tokens=row["input_tokens"],
        output_tokens=row["output_tokens"],
        latency_ms=row["latency_ms"],
        retrieval_ms=row["retrieval_ms"],
        created_at=row["created_at"],
    )


@router.get("/analytics/overview", response_model=Overview, summary="Read dashboard numbers")
def overview(user: User = Depends(require_user)):
    require(user.role, "analytics.read")
    with connect() as connection:
        return service.overview(connection, user)


@router.get("/insights/metrics", response_model=InsightMetrics, summary="Read computed insights")
def insight_metrics(user: User = Depends(require_user)):
    require(user.role, "insights.read")
    with connect() as connection:
        return service.insight_metrics(connection, user)


@router.post(
    "/insights/summaries", response_model=InsightSummary, summary="Create an advisory AI summary"
)
def insight_summary(user: User = Depends(require_user)):
    require(user.role, "insights.read")
    try:
        return service.insight_summary(user)
    except (AiUnavailable, AiOutputRejected):
        fail(503, "AI_UNAVAILABLE", "The AI summary is unavailable. The metrics are still correct.")


@router.get("/audit-events", response_model=AuditEventList, summary="Search the audit log")
def audit_events(user: User = Depends(require_user)):
    require(user.role, "audit.read")
    marks = ",".join("?" * len(user.hire_ids)) or "''"
    with connect() as connection:
        rows = connection.execute(
            f"SELECT * FROM audit_events WHERE hire_id IN ({marks}) "
            "ORDER BY created_at DESC, rowid DESC LIMIT 200",
            user.hire_ids,
        ).fetchall()
    return AuditEventList(
        items=[
            AuditEvent(
                id=row["id"],
                hire_id=row["hire_id"],
                actor_user_id=row["actor_user_id"],
                event_type=row["event_type"],
                summary=row["summary"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
    )


@router.get("/ai-runs", response_model=AiRunList, summary="List AI run records")
def ai_runs(user: User = Depends(require_user)):
    require(user.role, "audit.read")
    with connect() as connection:
        rows = connection.execute(
            "SELECT * FROM ai_runs ORDER BY created_at DESC, rowid DESC LIMIT 100"
        ).fetchall()
    return AiRunList(items=[_to_run(row) for row in rows])


@router.get("/ai-runs/{run_id}", response_model=AiRun, summary="Read one AI run record")
def ai_run(run_id: str, user: User = Depends(require_user)):
    require(user.role, "audit.read")
    with connect() as connection:
        row = connection.execute("SELECT * FROM ai_runs WHERE id=?", (run_id,)).fetchone()
    if row is None:
        not_found()
    return _to_run(row)


@router.get("/metrics", response_model=Metrics, summary="Read reliability metrics")
def metrics(user: User = Depends(require_user)):
    require(user.role, "metrics.read")
    with connect() as connection:
        return service.reliability_metrics(connection)


@router.get("/health/ai", response_model=AiHealth, summary="Read model configuration status")
def ai_health(user: User = Depends(require_user)):
    provider = current_provider()
    available = provider.name != "none"
    with connect() as connection:
        latest = connection.execute(
            "SELECT status, failure_reason FROM ai_runs WHERE status!='ABSTAINED' "
            "ORDER BY created_at DESC, rowid DESC LIMIT 1"
        ).fetchone()
    problem = latest["failure_reason"] if latest and latest["status"] == "UNAVAILABLE" else None
    if provider.is_stub:
        detail = "Offline rules are active. This is not a real AI model."
    elif not available:
        detail = (
            "No API key is set. Paste a Groq key after LLM_API_KEY= in the .env file. "
            "All manual workflows still work."
        )
    elif problem == "MODEL_RATE_LIMITED":
        detail = (
            "The last AI call hit the provider's limit. Wait a minute, or paste another key "
            "after LLM_API_KEY= in the .env file. No restart is needed."
        )
    elif problem == "MODEL_HTTP_401":
        detail = "The API key was rejected. Paste a valid key after LLM_API_KEY= in the .env file."
    elif problem:
        detail = "The last AI call failed. Manual workflows still work."
    else:
        detail = "A model is configured. To use your own key, change LLM_API_KEY in the .env file."
    return AiHealth(
        provider=provider.name,
        model=provider.model,
        available=available,
        is_stub=provider.is_stub,
        detail=detail,
    )
