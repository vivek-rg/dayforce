from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response

from app.ai.harness import AiOutputRejected, AiUnavailable
from app.auth.permissions import require
from app.auth.service import require_hire_scope, require_user
from app.documents import service
from app.planning.service import get_hire_row
from app.shared.contracts import (
    Document,
    DocumentCategory,
    DocumentExtraction,
    DocumentList,
    DocumentReviewRequest,
    Role,
    User,
)
from app.shared.db import connect
from app.shared.errors import fail, forbidden, not_found

router = APIRouter(tags=["documents"])


def _own_or_hr(connection, user: User, hire_id: str) -> None:
    require_hire_scope(user, hire_id)
    if user.role == Role.HR:
        return
    if (
        user.role != Role.EMPLOYEE
        or get_hire_row(connection, hire_id)["employee_user_id"] != user.id
    ):
        forbidden()


@router.post(
    "/hires/{hire_id}/documents",
    response_model=Document,
    status_code=201,
    summary="Upload a document",
)
async def upload(
    hire_id: str,
    category: DocumentCategory = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(require_user),
):
    with connect() as connection:
        _own_or_hr(connection, user, hire_id)
    data = await file.read(service.MAX_BYTES + 1)
    return service.save_upload(hire_id, category, file.filename or "document", data, user)


@router.get("/hires/{hire_id}/documents", response_model=DocumentList, summary="List documents")
def list_documents(hire_id: str, user: User = Depends(require_user)):
    with connect() as connection:
        _own_or_hr(connection, user, hire_id)
        rows = connection.execute(
            "SELECT * FROM documents WHERE hire_id=? ORDER BY created_at DESC, rowid DESC",
            (hire_id,),
        ).fetchall()
        return DocumentList(items=[service.to_document(connection, row) for row in rows])


@router.get("/documents/queue", response_model=DocumentList, summary="List documents to review")
def queue(user: User = Depends(require_user)):
    require(user.role, "document.queue")
    with connect() as connection:
        rows = connection.execute(
            "SELECT * FROM documents WHERE state IN ('SUBMITTED','UNDER_REVIEW') "
            "ORDER BY created_at, rowid"
        ).fetchall()
        return DocumentList(
            items=[
                service.to_document(connection, row)
                for row in rows
                if row["hire_id"] in user.hire_ids
            ]
        )


@router.get("/documents/{document_id}/content", summary="Stream a document to an authorized user")
def content(document_id: str, user: User = Depends(require_user)):
    with connect() as connection:
        row = connection.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        if row is None:
            not_found()
        _own_or_hr(connection, user, row["hire_id"])
    return Response(
        content=service.read_stored(row),
        media_type=row["mime_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{row["original_name"]}"',
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-store",
        },
    )


@router.post(
    "/documents/{document_id}/extractions",
    response_model=DocumentExtraction,
    status_code=201,
    summary="Run advisory AI extraction",
)
def extract(document_id: str, user: User = Depends(require_user)):
    require(user.role, "document.extract")
    try:
        return service.run_extraction(document_id, user)
    except (AiUnavailable, AiOutputRejected) as exc:
        fail(503, "AI_UNAVAILABLE", "AI extraction is unavailable. Review the document manually.")
        raise exc


@router.get(
    "/documents/{document_id}/extractions/latest",
    response_model=DocumentExtraction,
    summary="Read the latest advisory extraction",
)
def latest_extraction(document_id: str, user: User = Depends(require_user)):
    require(user.role, "document.extract")
    with connect() as connection:
        document = connection.execute(
            "SELECT hire_id FROM documents WHERE id=?", (document_id,)
        ).fetchone()
        if document is None or document["hire_id"] not in user.hire_ids:
            not_found()
        row = connection.execute(
            "SELECT e.*, r.model, r.provider FROM document_extractions e "
            "JOIN ai_runs r ON r.id=e.ai_run_id WHERE e.document_id=? "
            "ORDER BY e.created_at DESC, e.rowid DESC LIMIT 1",
            (document_id,),
        ).fetchone()
    if row is None:
        not_found()
    return service.to_extraction(row, row["model"], row["provider"] == "stub")


@router.post(
    "/documents/{document_id}/reviews",
    response_model=Document,
    summary="Verify, reject or request resubmission (human only)",
)
def review(document_id: str, body: DocumentReviewRequest, user: User = Depends(require_user)):
    require(user.role, "document.review")
    with connect() as connection:
        return service.review(
            connection, document_id, user, body.decision, body.reason, body.expected_version
        )
