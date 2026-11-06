from typing import Literal

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.auth.permissions import require
from app.auth.service import require_user
from app.knowledge import service
from app.notifications.service import notify, notify_role
from app.shared.contracts import (
    AssistantAnswer,
    AssistantQuestion,
    Escalation,
    EscalationAnswer,
    EscalationCreate,
    EscalationList,
    KnowledgeApprove,
    KnowledgeDocument,
    KnowledgeDocumentList,
    User,
)
from app.shared.db import connect
from app.shared.errors import fail, invalid_state, not_found
from app.shared.util import new_id, now_iso

router = APIRouter(tags=["knowledge"])
MAX_KNOWLEDGE_BYTES = 512 * 1024


def _to_escalation(row) -> Escalation:
    return Escalation(
        id=row["id"],
        raised_by=row["raised_by"],
        raised_by_name=row["raised_by_name"],
        question=row["question_text"],
        state=row["state"],
        resolution=row["resolution"],
        created_at=row["created_at"],
    )


ESCALATION_SELECT = (
    "SELECT e.*, u.display_name AS raised_by_name FROM hr_escalations e "
    "JOIN users u ON u.id=e.raised_by "
)


@router.post(
    "/assistant/questions",
    response_model=AssistantAnswer,
    summary="Ask the knowledge assistant",
)
def ask(body: AssistantQuestion, user: User = Depends(require_user)):
    return service.answer(body.question, user)


@router.post(
    "/assistant/escalations",
    response_model=Escalation,
    status_code=201,
    summary="Send an unanswered question to HR",
)
def escalate(body: EscalationCreate, user: User = Depends(require_user)):
    escalation_id = new_id("ESC")
    with connect() as connection:
        run = None
        if body.ai_run_id:
            run = connection.execute(
                "SELECT id FROM ai_runs WHERE id=? AND user_id=?", (body.ai_run_id, user.id)
            ).fetchone()
        connection.execute(
            "INSERT INTO hr_escalations (id, raised_by, ai_run_id, question_text, state, "
            "created_at) VALUES (?,?,?,?,'OPEN',?)",
            (escalation_id, user.id, run["id"] if run else None, body.question, now_iso()),
        )
        notify_role(
            connection,
            "HR",
            None,
            kind="ESCALATION",
            title="Question escalated from the assistant",
            body=body.question,
            dedupe_key=f"escalation:{escalation_id}",
        )
        row = connection.execute(ESCALATION_SELECT + "WHERE e.id=?", (escalation_id,)).fetchone()
    return _to_escalation(row)


@router.get(
    "/assistant/escalations", response_model=EscalationList, summary="List escalated questions"
)
def list_escalations(user: User = Depends(require_user)):
    require(user.role, "escalation.manage")
    with connect() as connection:
        rows = connection.execute(ESCALATION_SELECT + "ORDER BY e.created_at DESC").fetchall()
    return EscalationList(items=[_to_escalation(row) for row in rows])


@router.get(
    "/assistant/escalations/mine",
    response_model=EscalationList,
    summary="List questions I escalated",
)
def my_escalations(user: User = Depends(require_user)):
    with connect() as connection:
        rows = connection.execute(
            ESCALATION_SELECT + "WHERE e.raised_by=? ORDER BY e.created_at DESC", (user.id,)
        ).fetchall()
    return EscalationList(items=[_to_escalation(row) for row in rows])


@router.post(
    "/assistant/escalations/{escalation_id}/answers",
    response_model=Escalation,
    summary="Answer an escalated question",
)
def answer_escalation(
    escalation_id: str, body: EscalationAnswer, user: User = Depends(require_user)
):
    require(user.role, "escalation.manage")
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM hr_escalations WHERE id=?", (escalation_id,)
        ).fetchone()
        if row is None:
            not_found()
        if row["state"] != "OPEN":
            invalid_state("This question has already been answered.")
        connection.execute(
            "UPDATE hr_escalations SET state='ANSWERED', resolution=?, resolved_by=?, "
            "resolved_at=? WHERE id=? AND state='OPEN'",
            (body.answer, user.id, now_iso(), escalation_id),
        )
        notify(
            connection,
            row["raised_by"],
            "ESCALATION_ANSWERED",
            "HR answered your question",
            body.answer,
            f"escalation-answer:{escalation_id}",
        )
        updated = connection.execute(
            ESCALATION_SELECT + "WHERE e.id=?", (escalation_id,)
        ).fetchone()
    return _to_escalation(updated)


@router.get(
    "/knowledge/documents",
    response_model=KnowledgeDocumentList,
    summary="List knowledge sources I may see",
)
def list_documents(user: User = Depends(require_user)):
    with connect() as connection:
        return KnowledgeDocumentList(items=service.list_documents(connection, user))


@router.post(
    "/knowledge/documents",
    response_model=KnowledgeDocument,
    status_code=201,
    summary="Upload a draft knowledge document",
)
async def upload_document(
    title: str = Form(..., min_length=1, max_length=200),
    access_level: Literal["GENERAL", "MANAGER", "IT", "PAYROLL", "BENEFITS", "HR"] = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(require_user),
):
    require(user.role, "knowledge.manage")
    data = await file.read(MAX_KNOWLEDGE_BYTES + 1)
    if len(data) > MAX_KNOWLEDGE_BYTES:
        fail(413, "FILE_TOO_LARGE", "Knowledge documents must be 512 KB or smaller.")
    if not (file.filename or "").lower().endswith((".md", ".txt")):
        fail(415, "UNSUPPORTED_FILE", "Knowledge documents must be Markdown or text.")
    try:
        body = data.decode("utf-8")
    except UnicodeDecodeError:
        fail(415, "UNSUPPORTED_FILE", "Knowledge documents must be UTF-8 text.")
    if not body.strip() or "\x00" in body:
        fail(422, "VALIDATION_ERROR", "The document is empty or is not text.")
    with connect() as connection:
        return service.create_draft(connection, title, access_level, body, user.id)


@router.post(
    "/knowledge/documents/{document_id}/approve",
    response_model=KnowledgeDocument,
    summary="Approve a draft, making it searchable",
)
def approve_document(document_id: str, body: KnowledgeApprove, user: User = Depends(require_user)):
    require(user.role, "knowledge.manage")
    with connect() as connection:
        return service.approve(connection, document_id, body.version, user.id)
