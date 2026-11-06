import json

from fastapi import APIRouter, Depends

from app.actions import service
from app.actions.adapters import provisioning
from app.auth.permissions import require
from app.auth.service import require_hire_scope, require_user
from app.evidence.routes import to_source
from app.evidence.service import check_hire
from app.planning.service import get_hire_row
from app.shared.contracts import (
    AccessRequest,
    DecisionRequest,
    DecisionResult,
    EquipmentRequest,
    InvestigationContext,
    LocationAction,
    PreviewRequest,
    Proposal,
    ProposalList,
    ReservationAction,
    SourceRecord,
    User,
)
from app.shared.db import connect
from app.shared.errors import stale
from app.shared.util import audit, new_id, now_iso

router = APIRouter(tags=["actions"])


@router.get(
    "/review-inbox", response_model=ProposalList, summary="List exact proposals reviewer may see"
)
def review_inbox(user: User = Depends(require_user)):
    with connect() as connection:
        return ProposalList(items=service.review_inbox(connection, user))


@router.get("/proposals/{proposal_id}", response_model=Proposal, summary="Read one proposal")
def get_proposal(proposal_id: str, user: User = Depends(require_user)):
    with connect() as connection:
        proposal = service.get_proposal(connection, proposal_id)
    require_hire_scope(user, proposal.hire_id)
    return proposal


@router.post(
    "/hires/{hire_id}/change-previews",
    response_model=Proposal,
    status_code=201,
    summary="Create immutable reviewed-location proposal with plan diff",
)
def preview(hire_id: str, body: PreviewRequest, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    require(user.role, "proposal.location")
    with connect() as connection:
        hire = get_hire_row(connection, hire_id)
        if hire["profile_version"] != body.expected_profile_version:
            stale()
        case_id = service._active_or_manual_case(connection, hire_id, user)
        context = InvestigationContext(user=user, hire_id=hire_id, case_id=case_id)
        evidence = connection.execute(
            "SELECT id FROM evidence WHERE hire_id=? AND check_type='profile_location_confirmed' "
            "ORDER BY rowid DESC LIMIT 1",
            (hire_id,),
        ).fetchone()
        return service.save_proposal(
            connection,
            context,
            LocationAction(action_type="CHANGE_WORK_LOCATION", location_id=body.location_id),
            [evidence["id"]] if evidence else [],
        )


@router.post(
    "/hires/{hire_id}/equipment-requests",
    response_model=Proposal,
    status_code=201,
    summary="Request a device; creates a proposal for IT approval",
)
def request_equipment(hire_id: str, body: EquipmentRequest, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    require(user.role, "equipment.request")
    with connect() as connection:
        get_hire_row(connection, hire_id)
        case_id = service._active_or_manual_case(connection, hire_id, user)
        context = InvestigationContext(user=user, hire_id=hire_id, case_id=case_id)
        return service.save_proposal(
            connection,
            context,
            ReservationAction(
                action_type="RESERVE_EQUIPMENT", equipment_record_id=body.equipment_record_id
            ),
            [],
        )


@router.post(
    "/hires/{hire_id}/access-requests",
    response_model=SourceRecord,
    status_code=201,
    summary="Create a simulated account or access request",
)
def request_access(hire_id: str, body: AccessRequest, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    require(user.role, "access.request")
    payload = provisioning.request_access(hire_id, body.item, body.detail)
    source_id = new_id("it_access")
    with connect() as connection:
        hire = get_hire_row(connection, hire_id)
        connection.execute(
            "INSERT INTO source_records (id, hire_id, category, source_system, external_id, "
            "version, payload_json, observed_at, updated_by) VALUES (?,?,?,?,?,1,?,?,?)",
            (
                source_id,
                hire_id,
                "it_access",
                "demo",
                source_id,
                json.dumps(payload),
                now_iso(),
                user.id,
            ),
        )
        audit(connection, hire_id, "ACCESS_REQUESTED", f"{body.item} (simulated).", user.id)
        check_hire(connection, hire_id)
        row = connection.execute("SELECT * FROM source_records WHERE id=?", (source_id,)).fetchone()
        return to_source(row, hire["display_name"])


@router.post(
    "/proposals/{proposal_id}/decisions",
    response_model=DecisionResult,
    summary="Approve or reject exact immutable proposal",
)
def decide(proposal_id: str, body: DecisionRequest, user: User = Depends(require_user)):
    with connect() as connection:
        return service.decide(connection, proposal_id, user, body.decision, body.note)
