from fastapi import APIRouter

from app.shared.contracts import (
    DecisionRequest,
    DecisionResult,
    PreviewRequest,
    Proposal,
    ProposalList,
)
from app.shared.errors import not_implemented

router = APIRouter(tags=["actions"])


@router.get(
    "/review-inbox", response_model=ProposalList, summary="List exact proposals reviewer may see"
)
def review_inbox():
    # TODO P05: reviewer role + hire scope; include only actionable unexpired proposals.
    not_implemented()


@router.post(
    "/hires/{hire_id}/change-previews",
    response_model=Proposal,
    status_code=201,
    summary="Create immutable reviewed-location proposal with plan diff",
)
def preview(hire_id: str, body: PreviewRequest):
    # TODO P05: HR scoped; call planning preview; persist exact values and input versions.
    not_implemented()


@router.post(
    "/proposals/{proposal_id}/decisions",
    response_model=DecisionResult,
    summary="Approve or reject exact immutable proposal",
)
def decide(proposal_id: str, body: DecisionRequest):
    # TODO P05: reviewer/versions/expiry; durable approved action, never arbitrary tool.
    not_implemented()
