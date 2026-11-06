"""Metrics are SQL over application data. The model may only phrase them, never compute them."""

import json
import sqlite3
import statistics
from collections import deque
from datetime import date

from app.ai.harness import run_operation
from app.ai.prompts import INSIGHTS_SYSTEM, insights_user
from app.ai.validators import check_insight
from app.planning.service import load_tasks
from app.shared.contracts import (
    AuditEvent,
    CountItem,
    DisplayStatus,
    InsightEvidence,
    InsightMetric,
    InsightMetrics,
    InsightSummary,
    Metrics,
    OperationMetric,
    Overview,
    UpcomingJoiner,
    User,
)
from app.shared.db import connect
from app.shared.util import today

LATENCIES: deque[float] = deque(maxlen=2000)
counters = {"requests": 0, "errors": 0}


def record_request(milliseconds: float, status: int) -> None:
    LATENCIES.append(milliseconds)
    counters["requests"] += 1
    if status >= 500:
        counters["errors"] += 1


def _scoped_hires(connection, user: User) -> list:
    rows = connection.execute(
        "SELECT h.*, d.name AS department FROM hires h JOIN departments d ON d.id=h.department_id"
    ).fetchall()
    return [row for row in rows if row["id"] in user.hire_ids]


def overview(connection: sqlite3.Connection, user: User) -> Overview:
    hires = _scoped_hires(connection, user)
    all_tasks = [task for hire in hires for task in load_tasks(connection, hire["id"])]
    live = [t for t in all_tasks if t.work_state != "CANCELLED"]
    completed_hires = [hire for hire in hires if hire["completed_at"]]
    durations = [
        (
            date.fromisoformat(hire["completed_at"][:10])
            - date.fromisoformat(hire["created_at"][:10])
        ).days
        for hire in completed_hires
    ]

    def counts(values: list[str]) -> list[CountItem]:
        return [CountItem(label=label, count=values.count(label)) for label in sorted(set(values))]

    placeholders = ",".join("?" * len(hires)) or "''"
    ids = [hire["id"] for hire in hires]
    documents = connection.execute(
        f"SELECT COUNT(*) AS n FROM documents WHERE state IN ('SUBMITTED','UNDER_REVIEW') "
        f"AND hire_id IN ({placeholders})",
        ids,
    ).fetchone()["n"]
    equipment = connection.execute(
        "SELECT state FROM equipment_assets_v "
        f"WHERE assigned_hire_id IS NULL OR assigned_hire_id IN ({placeholders})",
        ids,
    ).fetchall()
    recent = connection.execute(
        f"SELECT * FROM audit_events WHERE hire_id IN ({placeholders}) "
        "ORDER BY created_at DESC, rowid DESC LIMIT 12",
        ids,
    ).fetchall()
    current = today().isoformat()
    upcoming = sorted(
        (hire for hire in hires if hire["start_date"] >= current),
        key=lambda hire: hire["start_date"],
    )[:6]
    return Overview(
        total_employees=len(hires),
        onboarding_in_progress=len(hires) - len(completed_hires),
        onboarding_completed=len(completed_hires),
        tasks_pending=sum(t.work_state != "COMPLETED" for t in live),
        tasks_overdue=sum(t.display_status == DisplayStatus.OVERDUE for t in live),
        documents_awaiting=documents,
        claims_without_proof=sum(
            t.work_state == "COMPLETED" and t.evidence_result in ("UNKNOWN", "BLOCKED")
            for t in live
        ),
        average_completion_days=round(statistics.mean(durations), 1) if durations else None,
        by_department=counts([hire["department"] for hire in hires]),
        by_location=counts([hire["location_id"] for hire in hires]),
        equipment=counts([row["state"] for row in equipment]),
        upcoming=[
            UpcomingJoiner(
                hire_id=hire["id"],
                display_name=hire["display_name"],
                start_date=hire["start_date"],
                location_id=hire["location_id"],
            )
            for hire in upcoming
        ],
        recent=[
            AuditEvent(
                id=row["id"],
                hire_id=row["hire_id"],
                actor_user_id=row["actor_user_id"],
                event_type=row["event_type"],
                summary=row["summary"],
                created_at=row["created_at"],
            )
            for row in recent
        ],
    )


def insight_metrics(connection: sqlite3.Connection, user: User) -> InsightMetrics:
    hires = _scoped_hires(connection, user)
    tasks = [task for hire in hires for task in load_tasks(connection, hire["id"])]
    live = [task for task in tasks if task.work_state != "CANCELLED"]

    def metric(identifier: str, label: str, items) -> InsightMetric:
        return InsightMetric(
            id=identifier,
            label=label,
            value=len(items),
            evidence=[
                InsightEvidence(ref=task.id, label=f"{task.title} ({task.hire_name})")
                for task in items[:6]
            ],
        )

    metrics = [
        metric(
            "overdue",
            "Overdue tasks",
            [t for t in live if t.display_status == DisplayStatus.OVERDUE],
        ),
        metric(
            "blocked",
            "Blocked tasks",
            [t for t in live if t.display_status == DisplayStatus.BLOCKED],
        ),
        metric(
            "unproven",
            "Tasks marked complete without proof",
            [
                t
                for t in live
                if t.work_state == "COMPLETED" and t.evidence_result in ("UNKNOWN", "BLOCKED")
            ],
        ),
    ]
    categories: dict[str, list] = {}
    for task in live:
        if task.display_status == DisplayStatus.OVERDUE:
            categories.setdefault(task.category.value, []).append(task)
    for category, items in sorted(categories.items()):
        metrics.append(metric(f"overdue_{category}", f"Overdue in {category}", items))
    ids = [hire["id"] for hire in hires]
    marks = ",".join("?" * len(ids)) or "''"
    rejected = connection.execute(
        "SELECT d.id, d.category, h.display_name FROM documents d JOIN hires h ON h.id=d.hire_id "
        f"WHERE d.state IN ('REJECTED','RESUBMISSION_REQUESTED') AND d.hire_id IN ({marks})",
        ids,
    ).fetchall()
    metrics.append(
        InsightMetric(
            id="document_issues",
            label="Documents rejected or sent back",
            value=len(rejected),
            evidence=[
                InsightEvidence(ref=row["id"], label=f"{row['category']} ({row['display_name']})")
                for row in rejected[:6]
            ],
        )
    )
    return InsightMetrics(metrics=metrics)


def insight_summary(user: User) -> InsightSummary:
    with connect() as connection:
        metrics = insight_metrics(connection, user)
    payload = [item.model_dump() for item in metrics.metrics]
    refs = {evidence.ref for item in metrics.metrics for evidence in item.evidence}
    values = {item.value for item in metrics.metrics}
    result = run_operation(
        "insights.summarize",
        [
            {"role": "system", "content": INSIGHTS_SYSTEM},
            {"role": "user", "content": insights_user(json.dumps(payload))},
        ],
        user_id=user.id,
        semantic_check=lambda output: check_insight(output, refs, values),
    )
    return InsightSummary(
        summary=result.output.summary,
        recommendations=result.output.recommendations,
        ai_run_id=result.run_id,
        model=result.model,
        is_stub=result.is_stub,
        metrics=metrics.metrics,
    )


def reliability_metrics(connection: sqlite3.Connection) -> Metrics:
    rows = connection.execute(
        "SELECT operation, COUNT(*) AS runs, "
        "SUM(status='VALIDATED') AS validated, SUM(status='ABSTAINED') AS abstained, "
        "SUM(status='REJECTED_OUTPUT') AS rejected, SUM(status='UNAVAILABLE') AS unavailable, "
        "AVG(latency_ms) AS latency, "
        "SUM(COALESCE(input_tokens,0)+COALESCE(output_tokens,0)) AS tokens "
        "FROM ai_runs GROUP BY operation ORDER BY operation"
    ).fetchall()
    retrieval = connection.execute(
        "SELECT AVG(retrieval_ms) AS value FROM ai_runs WHERE retrieval_ms IS NOT NULL"
    ).fetchone()["value"]
    work_failed = connection.execute(
        "SELECT COUNT(*) AS n FROM work_items WHERE state='FAILED'"
    ).fetchone()["n"]
    actions_failed = connection.execute(
        "SELECT COUNT(*) AS n FROM actions WHERE state='FAILED'"
    ).fetchone()["n"]
    tasks = connection.execute(
        "SELECT SUM(work_state='COMPLETED') AS done, COUNT(*) AS total FROM tasks "
        "WHERE work_state!='CANCELLED'"
    ).fetchone()
    samples = sorted(LATENCIES)
    return Metrics(
        api_requests=counters["requests"],
        api_p50_ms=round(statistics.median(samples), 1) if samples else 0.0,
        api_p95_ms=round(samples[int(len(samples) * 0.95) - 1], 1) if samples else 0.0,
        api_errors=counters["errors"],
        retrieval_average_ms=round(retrieval, 1) if retrieval is not None else None,
        operations=[
            OperationMetric(
                operation=row["operation"],
                runs=row["runs"],
                validated=row["validated"],
                abstained=row["abstained"],
                rejected=row["rejected"],
                unavailable=row["unavailable"],
                average_latency_ms=round(row["latency"] or 0, 1),
                total_tokens=row["tokens"],
            )
            for row in rows
        ],
        work_failed=work_failed,
        actions_failed=actions_failed,
        task_completion_rate=round((tasks["done"] or 0) / tasks["total"], 3)
        if tasks["total"]
        else 0.0,
    )
