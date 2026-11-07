from fastapi import APIRouter, Depends

from app.actions.service import get_proposal
from app.auth.permissions import require
from app.auth.service import require_hire_scope, require_user
from app.notifications.service import notify_role
from app.planning.service import get_hire_row, get_plan
from app.shared.contracts import (
    AcceptedWork,
    AnswerRequest,
    AuditEvent,
    Case,
    CaseCreate,
    CaseList,
    Question,
    QuestionList,
    Role,
    User,
    WorkItem,
)
from app.shared.db import connect
from app.shared.errors import forbidden, invalid_state, not_found
from app.shared.util import audit, audit_summary, new_id, now_iso

router = APIRouter(tags=["cases"])


def _to_question(row) -> Question:
    return Question(
        id=row["id"],
        case_id=row["case_id"],
        hire_name=row["hire_name"] if "hire_name" in row.keys() else None,
        recipient_user_id=row["recipient_user_id"],
        text=row["text"],
        state=row["state"],
        answer=row["answer"],
    )


def _queue(connection, case_id: str, kind: str, event_id: str) -> str:
    connection.execute(
        "INSERT OR IGNORE INTO work_items (id, event_id, case_id, kind, state, updated_at) "
        "VALUES (?,?,?,?,'PENDING',?)",
        (new_id("WRK"), event_id, case_id, kind, now_iso()),
    )
    return connection.execute("SELECT id FROM work_items WHERE event_id=?", (event_id,)).fetchone()[
        "id"
    ]


def _to_case(connection, row, user: User) -> Case:
    # The investigation transcript is never exposed. People see sanitized events and outcomes.
    questions = connection.execute(
        "SELECT * FROM questions WHERE case_id=? ORDER BY rowid", (row["id"],)
    ).fetchall()
    proposals = connection.execute(
        "SELECT id FROM proposals WHERE case_id=? ORDER BY rowid", (row["id"],)
    ).fetchall()
    evidence = get_plan(connection, row["hire_id"], user).checks
    timeline = connection.execute(
        "SELECT * FROM audit_events WHERE case_id=? ORDER BY created_at DESC, rowid DESC LIMIT 100",
        (row["id"],),
    ).fetchall()
    return Case(
        id=row["id"],
        hire_id=row["hire_id"],
        state=row["state"],
        kind=row["kind"],
        message=row["message"]
        if user.role == Role.HR or (user.role == Role.MANAGER and row["opened_by"] == user.id)
        else "",
        version=row["version"],
        model_calls=row["model_calls"],
        tool_calls=row["tool_calls"],
        questions=[
            _to_question(item)
            for item in questions
            if user.role == Role.HR or item["recipient_user_id"] == user.id
        ],
        proposals=[get_proposal(connection, item["id"]) for item in proposals],
        evidence=evidence,
        timeline=[
            AuditEvent(
                id=item["id"],
                hire_id=item["hire_id"],
                actor_user_id=item["actor_user_id"],
                event_type=item["event_type"],
                summary=audit_summary(item, user.role),
                created_at=item["created_at"],
            )
            for item in reversed(timeline)
        ],
    )


@router.post(
    "/hires/{hire_id}/cases",
    response_model=AcceptedWork,
    status_code=202,
    summary="Open or link investigation and queue work",
)
def create_case(hire_id: str, body: CaseCreate, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    require(user.role, "case.open")
    with connect() as connection:
        hire = get_hire_row(connection, hire_id)
        active = connection.execute(
            "SELECT * FROM cases WHERE hire_id=? AND state NOT IN ('RESOLVED','ESCALATED')",
            (hire_id,),
        ).fetchone()
        if active:
            if active["kind"] == "MANUAL":
                invalid_state("Finish the open approval for this hire first.")
            work = connection.execute(
                "SELECT id FROM work_items WHERE case_id=? ORDER BY rowid DESC LIMIT 1",
                (active["id"],),
            ).fetchone()
            return AcceptedWork(case_id=active["id"], work_item_id=work["id"])
        case_id = new_id("CASE")
        connection.execute(
            "INSERT INTO cases (id, hire_id, opened_by, message, state, kind, thread_id, "
            "created_at) VALUES (?,?,?,?,'OPEN','INVESTIGATION',?,?)",
            (case_id, hire_id, user.id, body.message, new_id("THREAD"), now_iso()),
        )
        audit(
            connection,
            hire_id,
            "CASE_OPENED",
            f"Investigation opened for {hire['display_name']}.",
            user.id,
            case_id,
        )
        work_id = _queue(connection, case_id, "INVESTIGATE", f"investigate:{case_id}")
    return AcceptedWork(case_id=case_id, work_item_id=work_id)


@router.get("/hires/{hire_id}/cases", response_model=CaseList, summary="List a hire's cases")
def list_cases(hire_id: str, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    require(user.role, "case.open")
    with connect() as connection:
        rows = connection.execute(
            "SELECT * FROM cases WHERE hire_id=? ORDER BY created_at DESC, rowid DESC", (hire_id,)
        ).fetchall()
        return CaseList(items=[_to_case(connection, row, user) for row in rows])


@router.get(
    "/cases/{case_id}", response_model=Case, summary="Read scoped case and sanitized timeline"
)
def get_case(case_id: str, user: User = Depends(require_user)):
    with connect() as connection:
        row = connection.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None:
            not_found()
        require_hire_scope(user, row["hire_id"])
        return _to_case(connection, row, user)


@router.get("/questions", response_model=QuestionList, summary="List questions waiting for me")
def my_questions(user: User = Depends(require_user)):
    with connect() as connection:
        rows = connection.execute(
            "SELECT q.*, c.hire_id, h.display_name AS hire_name FROM questions q "
            "JOIN cases c ON c.id=q.case_id JOIN hires h ON h.id=c.hire_id "
            "WHERE q.recipient_user_id=? AND q.state='PENDING' ORDER BY q.rowid",
            (user.id,),
        ).fetchall()
    return QuestionList(
        items=[_to_question(row) for row in rows if row["hire_id"] in user.hire_ids]
    )


@router.post(
    "/questions/{question_id}/responses",
    response_model=AcceptedWork,
    status_code=202,
    summary="Answer intended question and queue resume",
)
def answer_question(question_id: str, body: AnswerRequest, user: User = Depends(require_user)):
    """An answer is information for the investigation. It is never an approval."""
    with connect() as connection:
        row = connection.execute(
            "SELECT q.*, c.hire_id FROM questions q JOIN cases c ON c.id=q.case_id WHERE q.id=?",
            (question_id,),
        ).fetchone()
        if row is None:
            not_found()
        require_hire_scope(user, row["hire_id"])
        if row["recipient_user_id"] != user.id:
            forbidden()
        event = f"resume:answer:{question_id}"
        if row["state"] == "ANSWERED":
            if row["answer"] != body.answer:
                invalid_state("A different answer is already recorded.")
            work_id = _queue(connection, row["case_id"], "RESUME", event)
            return AcceptedWork(case_id=row["case_id"], work_item_id=work_id)
        if row["state"] != "PENDING":
            invalid_state("This question is closed.")
        connection.execute(
            "UPDATE questions SET state='ANSWERED', answer=?, answered_by=?, answered_at=? "
            "WHERE id=? AND state='PENDING'",
            (body.answer, user.id, now_iso(), question_id),
        )
        connection.execute(
            "UPDATE cases SET state='INVESTIGATING', version=version+1 WHERE id=?",
            (row["case_id"],),
        )
        audit(
            connection,
            row["hire_id"],
            "QUESTION_ANSWERED",
            "The clarification was answered. Official records did not change.",
            user.id,
            row["case_id"],
        )
        work_id = _queue(connection, row["case_id"], "RESUME", event)
    return AcceptedWork(case_id=row["case_id"], work_item_id=work_id)


@router.get(
    "/work-items/{work_item_id}", response_model=WorkItem, summary="Poll scoped durable work"
)
def get_work_item(work_item_id: str, user: User = Depends(require_user)):
    with connect() as connection:
        row = connection.execute(
            "SELECT w.*, c.hire_id FROM work_items w JOIN cases c ON c.id=w.case_id WHERE w.id=?",
            (work_item_id,),
        ).fetchone()
    if row is None:
        not_found()
    require_hire_scope(user, row["hire_id"])
    return WorkItem(
        id=row["id"],
        case_id=row["case_id"],
        kind=row["kind"],
        state=row["state"],
        attempts=row["attempts"],
        updated_at=row["updated_at"],
    )


__all__ = ["router", "notify_role"]
