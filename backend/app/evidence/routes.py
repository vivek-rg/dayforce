import json

from fastapi import APIRouter, Depends, Query

from app.auth.permissions import CATEGORY_VIEW, SOURCE_WRITERS, require
from app.auth.service import require_hire_scope, require_user
from app.evidence.service import check_hire
from app.planning.service import get_hire_row, refresh_completion
from app.shared.contracts import (
    Category,
    EvidenceList,
    Role,
    SourceRecord,
    SourceRecordList,
    SourceWrite,
    User,
)
from app.shared.db import connect
from app.shared.errors import fail, forbidden, invalid_state, not_found, stale
from app.shared.util import audit, now_iso

router = APIRouter(tags=["evidence"])


def to_source(row, hire_name: str | None = None) -> SourceRecord:
    return SourceRecord(
        id=row["id"],
        hire_id=row["hire_id"],
        hire_name=hire_name,
        version=row["version"],
        observed_at=row["observed_at"],
        payload=json.loads(row["payload_json"]),
    )


@router.post(
    "/hires/{hire_id}/checks", response_model=EvidenceList, summary="Run deterministic checks"
)
def run_checks(hire_id: str, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    require(user.role, "checks.run")
    with connect() as connection:
        items = check_hire(connection, hire_id)
        refresh_completion(connection, hire_id)
    return EvidenceList(items=items)


@router.get("/sources", response_model=SourceRecordList, summary="List simulated-system records")
def list_sources(category: Category = Query(...), user: User = Depends(require_user)):
    allowed = CATEGORY_VIEW.get(user.role)
    if allowed is not None and category.value not in allowed:
        forbidden()
    if user.role == Role.EMPLOYEE and category == Category.DOCUMENTS:
        forbidden()
    include_inventory = category == Category.EQUIPMENT and user.role in (Role.IT, Role.HR)
    with connect() as connection:
        rows = connection.execute(
            "SELECT s.*, h.display_name AS hire_name FROM source_records s "
            "LEFT JOIN hires h ON h.id=s.hire_id WHERE s.category=? ORDER BY s.id",
            (category.value,),
        ).fetchall()
    return SourceRecordList(
        items=[
            to_source(row, row["hire_name"])
            for row in rows
            if row["hire_id"] in user.hire_ids or (row["hire_id"] is None and include_inventory)
        ]
    )


def _validate_payload(connection, user: User, hire, payload, existing) -> None:
    if user.role not in SOURCE_WRITERS[payload.category]:
        forbidden()
    if payload.category == "equipment":
        if payload.state == "RESERVED":
            invalid_state("Reservations need an approved proposal. Request equipment instead.")
        if payload.state == "HANDED_OVER" and (
            payload.assignee_hire_id != hire["id"] or payload.handover_at is None
        ):
            fail(422, "VALIDATION_ERROR", "Handover needs this hire as assignee and a time.")
        if payload.state == "AVAILABLE" and (payload.assignee_hire_id or payload.handover_at):
            fail(422, "VALIDATION_ERROR", "An available device cannot have an assignee.")
    if payload.category == "payroll" and payload.setup_confirmed and not payload.profile_created:
        fail(422, "VALIDATION_ERROR", "Payroll setup cannot be confirmed without a profile.")
    if payload.category == "benefits" and user.role == Role.EMPLOYEE:
        if hire["employee_user_id"] != user.id or payload.state != "DECLINED":
            forbidden()
    if payload.category == "manager":
        if hire["manager_user_id"] != user.id:
            forbidden()
        buddy = connection.execute(
            "SELECT 1 FROM users WHERE id=? AND active=1", (payload.buddy_user_id,)
        ).fetchone()
        if buddy is None:
            fail(422, "VALIDATION_ERROR", "Buddy must be an active user.")


@router.put(
    "/hires/{hire_id}/sources/{source_id}",
    response_model=SourceRecord,
    summary="Record a typed simulated-system observation",
)
def write_source(
    hire_id: str, source_id: str, body: SourceWrite, user: User = Depends(require_user)
):
    require_hire_scope(user, hire_id)
    with connect() as connection:
        hire = get_hire_row(connection, hire_id)
        existing = connection.execute(
            "SELECT * FROM source_records WHERE id=?", (source_id,)
        ).fetchone()
        _validate_payload(connection, user, hire, body.payload, existing)
        payload_json = body.payload.model_dump_json()
        if existing is None:
            if body.expected_version != 0:
                not_found()
            connection.execute(
                "INSERT INTO source_records (id, hire_id, category, source_system, external_id, "
                "version, payload_json, observed_at, updated_by) VALUES (?,?,?,?,?,1,?,?,?)",
                (
                    source_id,
                    hire_id,
                    body.payload.category,
                    "demo",
                    source_id,
                    payload_json,
                    now_iso(),
                    user.id,
                ),
            )
        else:
            if existing["hire_id"] != hire_id:
                not_found()
            if existing["category"] != body.payload.category:
                invalid_state("A record cannot change category.")
            cursor = connection.execute(
                "UPDATE source_records SET payload_json=?, version=version+1, observed_at=?, "
                "updated_by=? WHERE id=? AND version=?",
                (payload_json, now_iso(), user.id, source_id, body.expected_version),
            )
            if cursor.rowcount != 1:
                stale()
        audit(
            connection,
            hire_id,
            "SOURCE_RECORDED",
            f"{body.payload.category} record updated ({source_id}).",
            user.id,
        )
        check_hire(connection, hire_id)
        refresh_completion(connection, hire_id)
        row = connection.execute("SELECT * FROM source_records WHERE id=?", (source_id,)).fetchone()
    return to_source(row, hire["display_name"])
