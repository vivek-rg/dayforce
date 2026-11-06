"""Upload checks, private storage and human review. AI output here is advisory only."""

import hashlib
import io
import json
import re
import sqlite3
import uuid
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from app.ai.harness import run_operation
from app.ai.prompts import EXTRACTION_SYSTEM, extraction_user
from app.ai.providers import current_provider
from app.ai.validators import check_extraction
from app.auth.permissions import SENSITIVE_DOCUMENTS
from app.evidence.service import check_hire
from app.notifications.service import notify, notify_role
from app.planning.service import get_hire_row, refresh_completion
from app.shared.config import documents_path
from app.shared.contracts import (
    Document,
    DocumentExtraction,
    DocumentReview,
    ExtractedField,
    Mismatch,
    User,
)
from app.shared.errors import fail, invalid_state, not_found, stale
from app.shared.util import audit, new_id, now_iso

MAX_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 20
MAX_TEXT_CHARS = 12000
ALLOWED = {
    ".pdf": ("application/pdf", lambda data: data.startswith(b"%PDF-")),
    ".png": ("image/png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    ".jpg": ("image/jpeg", lambda data: data.startswith(b"\xff\xd8\xff")),
    ".jpeg": ("image/jpeg", lambda data: data.startswith(b"\xff\xd8\xff")),
    ".txt": ("text/plain", lambda data: _is_text(data)),
}
LOCATION_NAMES = {
    "BLR-DEMO": ("bengaluru", "bangalore", "blr-demo"),
    "HYD-DEMO": ("hyderabad", "hyd-demo"),
}
LOCATION_LINE = re.compile(r"(work location|place of posting|based (in|at)|location)", re.I)


def _is_text(data: bytes) -> bool:
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def safe_name(name: str) -> str:
    """Display only. The stored path is always random and never comes from the user."""
    cleaned = re.sub(r"[^A-Za-z0-9._ -]", "_", Path(name.replace("\\", "/")).name).strip(". ")
    return cleaned[:150] or "document"


def validate_upload(name: str, data: bytes) -> str:
    if not data:
        fail(422, "VALIDATION_ERROR", "The file is empty.")
    if len(data) > MAX_BYTES:
        fail(413, "FILE_TOO_LARGE", "Files must be 5 MB or smaller.")
    rule = ALLOWED.get(Path(name).suffix.lower())
    if rule is None:
        fail(415, "UNSUPPORTED_FILE", "Allowed types are PDF, PNG, JPEG and TXT.")
    mime, matches = rule
    if not matches(data):
        fail(415, "UNSUPPORTED_FILE", "The file's contents do not match its type.")
    return mime


def extract_text(mime: str, data: bytes) -> str | None:
    """Text for PDFs with a text layer and plain text. Scanned files go to manual review: no OCR."""
    if mime == "text/plain":
        return data.decode("utf-8")[:MAX_TEXT_CHARS]
    if mime != "application/pdf":
        return None
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted or len(reader.pages) > MAX_PDF_PAGES:
            return None
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except (PyPdfError, ValueError, KeyError, TypeError, OSError):
        return None
    return text[:MAX_TEXT_CHARS] if text.strip() else None


def detect_location(text: str | None) -> str | None:
    """Plain code, not a model. Prefer a labelled line, otherwise a single unambiguous mention."""
    if not text:
        return None

    def found(fragment: str) -> set[str]:
        lowered = fragment.lower()
        return {
            location
            for location, names in LOCATION_NAMES.items()
            if any(name in lowered for name in names)
        }

    for line in text.splitlines():
        if LOCATION_LINE.search(line):
            matches = found(line)
            if len(matches) == 1:
                return matches.pop()
    matches = found(text)
    return matches.pop() if len(matches) == 1 else None


def _reviews(connection, document_id: str) -> list[DocumentReview]:
    return [
        DocumentReview(
            id=row["id"],
            reviewer_user_id=row["reviewer_user_id"],
            decision=row["decision"],
            reason=row["reason"],
            created_at=row["created_at"],
        )
        for row in connection.execute(
            "SELECT * FROM document_reviews WHERE document_id=? ORDER BY created_at, rowid",
            (document_id,),
        )
    ]


def to_document(connection, row) -> Document:
    hire = connection.execute(
        "SELECT display_name FROM hires WHERE id=?", (row["hire_id"],)
    ).fetchone()
    return Document(
        id=row["id"],
        hire_id=row["hire_id"],
        hire_name=hire["display_name"],
        category=row["category"],
        state=row["state"],
        original_name=row["original_name"],
        mime_type=row["mime_type"],
        size_bytes=row["size_bytes"],
        text_available=bool(row["text_available"]),
        declared_location_id=row["declared_location_id"],
        version=row["version"],
        created_at=row["created_at"],
        reviews=_reviews(connection, row["id"]),
    )


def save_upload(hire_id: str, category: str, name: str, data: bytes, user: User) -> Document:
    mime = validate_upload(name, data)
    digest = hashlib.sha256(data).hexdigest()
    text = extract_text(mime, data)
    from app.shared.db import connect

    folder = documents_path()
    folder.mkdir(parents=True, exist_ok=True)
    key = uuid.uuid4().hex
    temporary = folder / f"{key}.tmp"
    temporary.write_bytes(data)
    try:
        with connect() as connection:
            if connection.execute(
                "SELECT 1 FROM documents WHERE hire_id=? AND category=? AND sha256=?",
                (hire_id, category, digest),
            ).fetchone():
                fail(409, "DUPLICATE_DOCUMENT", "This exact file was already submitted.")
            active = connection.execute(
                "SELECT id, state FROM documents WHERE hire_id=? AND category=? "
                "AND state!='SUPERSEDED'",
                (hire_id, category),
            ).fetchall()
            if any(item["state"] == "VERIFIED" for item in active):
                invalid_state("This category is already verified.")
            for item in active:
                connection.execute(
                    "UPDATE documents SET state='SUPERSEDED', version=version+1 WHERE id=?",
                    (item["id"],),
                )
            document_id = new_id("DOC")
            connection.execute(
                "INSERT INTO documents (id, hire_id, category, state, storage_key, sha256, "
                "mime_type, size_bytes, original_name, text_available, declared_location_id, "
                "uploaded_by, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    document_id,
                    hire_id,
                    category,
                    "SUBMITTED",
                    key,
                    digest,
                    mime,
                    len(data),
                    safe_name(name),
                    int(bool(text)),
                    detect_location(text) if category == "signed_employment" else None,
                    user.id,
                    now_iso(),
                ),
            )
            audit(connection, hire_id, "DOCUMENT_SUBMITTED", f"{category} submitted.", user.id)
            check_hire(connection, hire_id)
            notify_role(
                connection,
                "HR",
                hire_id,
                kind="APPROVAL_REQUEST",
                title="Document awaiting review",
                body=f"{category.replace('_', ' ')} for review",
                dedupe_key=f"doc:{document_id}",
            )
            row = connection.execute(
                "SELECT * FROM documents WHERE id=?", (document_id,)
            ).fetchone()
            document = to_document(connection, row)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    temporary.replace(folder / key)
    return document


def read_stored(row) -> bytes:
    path = documents_path() / row["storage_key"]
    if not path.is_file():
        not_found()
    return path.read_bytes()


def review(
    connection: sqlite3.Connection,
    document_id: str,
    user: User,
    decision: str,
    reason: str,
    expected: int,
) -> Document:
    """The only path to VERIFIED, and it requires a person."""
    row = connection.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
    if row is None or row["hire_id"] not in user.hire_ids:
        not_found()
    if row["version"] != expected:
        stale()
    if row["state"] not in ("SUBMITTED", "UNDER_REVIEW"):
        invalid_state("This document is not awaiting review.")
    if decision != "VERIFY" and not reason.strip():
        fail(422, "VALIDATION_ERROR", "Give a reason so the employee knows what to fix.")
    states = {
        "VERIFY": "VERIFIED",
        "REJECT": "REJECTED",
        "REQUEST_RESUBMISSION": "RESUBMISSION_REQUESTED",
    }
    cursor = connection.execute(
        "UPDATE documents SET state=?, version=version+1 WHERE id=? AND version=?",
        (states[decision], document_id, expected),
    )
    if cursor.rowcount != 1:
        stale()
    connection.execute(
        "INSERT INTO document_reviews (id, document_id, reviewer_user_id, decision, reason, "
        "created_at) VALUES (?,?,?,?,?,?)",
        (new_id("REV"), document_id, user.id, decision, reason.strip(), now_iso()),
    )
    audit(
        connection,
        row["hire_id"],
        "DOCUMENT_" + states[decision],
        f"{row['category']} reviewed by {user.display_name}.",
        user.id,
    )
    hire = get_hire_row(connection, row["hire_id"])
    if hire["employee_user_id"]:
        title = {
            "VERIFY": "Document verified",
            "REJECT": "Document rejected",
            "REQUEST_RESUBMISSION": "Please resubmit a document",
        }[decision]
        notify(
            connection,
            hire["employee_user_id"],
            "DOCUMENT_" + states[decision],
            title,
            reason.strip() or row["category"].replace("_", " "),
            f"doc-review:{document_id}:{expected}",
            hire_id=row["hire_id"],
        )
    check_hire(connection, row["hire_id"])
    refresh_completion(connection, row["hire_id"])
    return to_document(
        connection,
        connection.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone(),
    )


def _field_mismatches(fields: list[ExtractedField], hire) -> list[Mismatch]:
    """Code, not the model, decides whether a document disagrees with the profile."""
    mismatches = []
    for field in fields:
        name = field.name.lower()
        if "location" in name:
            location = detect_location(field.value)
            if location and location != hire["location_id"]:
                mismatches.append(
                    Mismatch(
                        field="work_location",
                        document_value=field.value,
                        profile_value=hire["location_id"],
                    )
                )
        elif "name" in name and hire["display_name"].lower() not in field.value.lower():
            mismatches.append(
                Mismatch(
                    field="employee_name",
                    document_value=field.value,
                    profile_value=hire["display_name"],
                )
            )
        elif (
            ("joining" in name or "start" in name)
            and re.search(r"\d{4}", field.value)
            and hire["start_date"] not in field.value
        ):
            mismatches.append(
                Mismatch(
                    field="joining_date",
                    document_value=field.value,
                    profile_value=hire["start_date"],
                )
            )
    return mismatches


def to_extraction(row, model: str, is_stub: bool) -> DocumentExtraction:
    return DocumentExtraction(
        id=row["id"],
        document_id=row["document_id"],
        suggested_category=row["suggested_category"],
        fields=json.loads(row["fields_json"]),
        missing=json.loads(row["missing_json"]),
        mismatches=json.loads(row["mismatches_json"]),
        summary=row["summary"],
        ai_run_id=row["ai_run_id"],
        model=model,
        is_stub=is_stub,
        created_at=row["created_at"],
    )


def run_extraction(document_id: str, user: User) -> DocumentExtraction:
    """No transaction stays open during inference. Nothing here changes the document's state."""
    from app.shared.db import connect

    with connect() as connection:
        row = connection.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        if row is None or row["hire_id"] not in user.hire_ids:
            not_found()
        hire = get_hire_row(connection, row["hire_id"])
    if row["category"] in SENSITIVE_DOCUMENTS and not current_provider().is_local:
        fail(
            409,
            "AI_BLOCKED_SENSITIVE",
            "This category is never sent to a hosted model. Review it manually.",
        )
    text = extract_text(row["mime_type"], read_stored(row))
    if not text:
        fail(409, "NO_TEXT_LAYER", "No readable text was found, so this needs manual review.")
    result = run_operation(
        "document.extract",
        [
            {"role": "system", "content": EXTRACTION_SYSTEM},
            {"role": "user", "content": extraction_user(row["category"], text)},
        ],
        user_id=user.id,
        hire_id=row["hire_id"],
        semantic_check=lambda output: check_extraction(output, text),
    )
    output = result.output
    mismatches = _field_mismatches(output.fields, hire)
    extraction_id = new_id("EXT")
    with connect() as connection:
        connection.execute(
            "INSERT INTO document_extractions (id, document_id, ai_run_id, suggested_category, "
            "fields_json, missing_json, mismatches_json, summary, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                extraction_id,
                document_id,
                result.run_id,
                output.suggested_category,
                json.dumps([field.model_dump() for field in output.fields]),
                json.dumps(output.missing),
                json.dumps([item.model_dump() for item in mismatches]),
                output.summary,
                now_iso(),
            ),
        )
        if row["state"] == "SUBMITTED":
            connection.execute(
                "UPDATE documents SET state='UNDER_REVIEW', version=version+1 "
                "WHERE id=? AND state='SUBMITTED'",
                (document_id,),
            )
        saved = connection.execute(
            "SELECT * FROM document_extractions WHERE id=?", (extraction_id,)
        ).fetchone()
    return to_extraction(saved, result.model, result.is_stub)
