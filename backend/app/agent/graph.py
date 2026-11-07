"""One bounded investigation. Every wait and counter lives in application tables.

The loop is rebuilt from stored steps plus fresh records on each run, so a restart during a human
wait loses nothing. That made a framework checkpointer unnecessary for this one linear loop.
"""

import hashlib
import json
import time

from fastapi import HTTPException

from app.actions.service import save_proposal
from app.agent.model_client import generate_next_step
from app.agent.tools import ScopeLost, dispatch_read
from app.ai.harness import AiOutputRejected, AiUnavailable
from app.auth.service import load_user
from app.notifications.service import notify, notify_role
from app.shared.config import int_setting
from app.shared.contracts import AskStep, FinishStep, InvestigationContext, ProposeStep, ReadStep
from app.shared.db import connect
from app.shared.util import audit, new_id, now_iso


def _add_step(connection, case_id: str, kind: str, summary: str, observed: dict) -> None:
    position = connection.execute(
        "SELECT COALESCE(MAX(position), 0) + 1 AS next FROM case_steps WHERE case_id=?", (case_id,)
    ).fetchone()["next"]
    connection.execute(
        "INSERT INTO case_steps (id, case_id, position, kind, summary, observed_json, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (new_id("STP"), case_id, position, kind, summary[:300], json.dumps(observed), now_iso()),
    )


def build_steps(connection, case_id: str) -> list[dict]:
    """Stored reads plus current answers and proposal outcomes, ordered for the model."""
    steps = []
    for row in connection.execute(
        "SELECT kind, summary, observed_json FROM case_steps WHERE case_id=? ORDER BY position",
        (case_id,),
    ):
        steps.append(
            {"kind": row["kind"], "summary": row["summary"], **json.loads(row["observed_json"])}
        )
    for row in connection.execute(
        "SELECT text, answer FROM questions WHERE case_id=? AND state='ANSWERED' ORDER BY rowid",
        (case_id,),
    ):
        steps.append({"kind": "answer", "question": row["text"], "answer": row["answer"]})
    for row in connection.execute(
        "SELECT p.action_type, d.decision, a.state, a.observed_json FROM proposals p "
        "LEFT JOIN decisions d ON d.proposal_id=p.id LEFT JOIN actions a ON a.proposal_id=p.id "
        "WHERE p.case_id=? ORDER BY p.rowid",
        (case_id,),
    ):
        steps.append(
            {
                "kind": "proposal",
                "action_type": row["action_type"],
                "decision": row["decision"],
                "action_state": row["state"],
                "observed": json.loads(row["observed_json"]) if row["observed_json"] else {},
            }
        )
    return steps


def _set_state(connection, case_id: str, state: str) -> None:
    connection.execute("UPDATE cases SET state=?, version=version+1 WHERE id=?", (state, case_id))


def _escalate(case: dict, reason: str) -> None:
    with connect() as connection:
        _set_state(connection, case["id"], "ESCALATED")
        audit(
            connection,
            case["hire_id"],
            "CASE_ESCALATED",
            f"{reason} Manual onboarding work is unaffected.",
            case_id=case["id"],
        )
        notify_role(
            connection,
            "HR",
            case["hire_id"],
            kind="ESCALATION",
            title="Investigation needs a person",
            body=reason,
            dedupe_key=f"case-escalated:{case['id']}",
        )


def _claim_model_attempt(case_id: str, limit: int) -> bool:
    with connect() as connection:
        cursor = connection.execute(
            "UPDATE cases SET model_calls=model_calls+1 WHERE id=? AND model_calls<?",
            (case_id, limit),
        )
        return cursor.rowcount == 1


def _recipient(connection, role: str, hire_id: str) -> str | None:
    row = connection.execute(
        "SELECT u.id FROM users u JOIN user_scopes s ON s.user_id=u.id "
        "WHERE u.role=? AND u.active=1 AND s.hire_id=? ORDER BY u.id LIMIT 1",
        (role, hire_id),
    ).fetchone()
    return row["id"] if row else None


def run_investigation(case_id: str) -> None:
    """Runs until the case waits on a person, finishes, or hits a budget."""
    max_calls = int_setting("MAX_MODEL_CALLS", 12)
    max_reads = int_setting("MAX_TOOL_CALLS", 16)
    deadline = time.monotonic() + int_setting("INVESTIGATION_TIMEOUT_SECONDS", 90)
    with connect() as connection:
        row = connection.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None or row["state"] in ("RESOLVED", "ESCALATED"):
            return
        case = dict(row)
        user = load_user(connection, case["opened_by"])
        if user is None or case["hire_id"] not in user.hire_ids:
            user = None
        else:
            _set_state(connection, case_id, "INVESTIGATING")
    if user is None:
        _escalate(case, "The person who opened this case no longer has access.")
        return
    context = InvestigationContext(user=user, hire_id=case["hire_id"], case_id=case_id)
    while True:
        if time.monotonic() > deadline:
            _escalate(case, "The investigation reached its time limit.")
            return
        with connect() as connection:
            steps = build_steps(connection, case_id)
        try:
            # No transaction is held during inference.
            result = generate_next_step(
                case["message"],
                json.dumps(steps)[-24000:],
                user_id=user.id,
                hire_id=case["hire_id"],
                case_id=case_id,
                before_attempt=lambda: _claim_model_attempt(case_id, max_calls),
            )
        except AiUnavailable:
            _escalate(case, "The AI model is unavailable, so a person should take this case.")
            return
        except AiOutputRejected as exc:
            reason = (
                "The investigation used all its model calls."
                if exc.reason == "BUDGET_EXHAUSTED"
                else "The model's output failed validation."
            )
            _escalate(case, reason)
            return
        step = result.output.next_step
        if isinstance(step, ReadStep):
            with connect() as connection:
                allowed = connection.execute(
                    "UPDATE cases SET tool_calls=tool_calls+1 WHERE id=? AND tool_calls<?",
                    (case_id, max_reads),
                ).rowcount
            if not allowed:
                _escalate(case, "The investigation used all its read calls.")
                return
            try:
                observation = dispatch_read(step.tool, context)
            except ScopeLost:
                _escalate(case, "The person who opened this case no longer has access.")
                return
            with connect() as connection:
                _add_step(
                    connection,
                    case_id,
                    "read",
                    step.reason_summary,
                    {
                        "tool": step.tool,
                        "facts": observation.facts,
                        "evidence": [
                            {"id": e.id, "check": e.check_type, "result": e.result.value}
                            for e in observation.evidence
                        ],
                        "untrusted_text": observation.untrusted_text,
                    },
                )
            continue
        if isinstance(step, AskStep):
            key = hashlib.sha256(step.question.encode()).hexdigest()[:24]
            with connect() as connection:
                recipient = _recipient(connection, step.recipient_role.value, case["hire_id"])
                if recipient is None:
                    recipient = _recipient(connection, "HR", case["hire_id"])
                if recipient is None:
                    recipient = None
                else:
                    question_id = new_id("QST")
                    connection.execute(
                        "INSERT OR IGNORE INTO questions (id, case_id, dedupe_key, "
                        "recipient_user_id, text, state) VALUES (?,?,?,?,?,'PENDING')",
                        (question_id, case_id, key, recipient, step.question),
                    )
                    existing = connection.execute(
                        "SELECT state FROM questions WHERE case_id=? AND dedupe_key=?",
                        (case_id, key),
                    ).fetchone()
                    # Check under the write lock: recorded answers are already in build_steps.
                    if existing["state"] != "PENDING":
                        continue
                    _set_state(connection, case_id, "WAITING_HUMAN")
                    audit(
                        connection,
                        case["hire_id"],
                        "QUESTION_ASKED",
                        "A responsible person was asked to clarify. The case is paused.",
                        case_id=case_id,
                    )
                    notify(
                        connection,
                        recipient,
                        "QUESTION",
                        "Your input is needed",
                        step.question,
                        f"question:{case_id}:{key}",
                        hire_id=case["hire_id"],
                    )
            if recipient is None:
                _escalate(case, "Nobody with access could be asked.")
            return
        if isinstance(step, ProposeStep):
            with connect() as connection:
                try:
                    save_proposal(connection, context, step.payload, step.evidence_ids)
                except HTTPException as exc:
                    _add_step(
                        connection,
                        case_id,
                        "rejected_proposal",
                        "The server rejected that proposal.",
                        {
                            "error": exc.detail.get("code")
                            if isinstance(exc.detail, dict)
                            else "ERROR"
                        },
                    )
                    continue
                _set_state(connection, case_id, "WAITING_APPROVAL")
            return
        if isinstance(step, FinishStep):
            if step.step == "escalate":
                _escalate(case, step.reason_summary)
                return
            with connect() as connection:
                _set_state(connection, case_id, "RESOLVED")
                audit(
                    connection,
                    case["hire_id"],
                    "CASE_RESOLVED",
                    step.reason_summary,
                    case_id=case_id,
                )
            return
