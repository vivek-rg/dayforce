from fastapi import APIRouter

from app.shared.contracts import EvidenceList, SourceRecord, SourceWrite
from app.shared.errors import not_implemented

router = APIRouter(tags=["evidence"])


@router.post(
    "/hires/{hire_id}/checks", response_model=EvidenceList, summary="Run deterministic checks"
)
def run_checks(hire_id: str):
    # TODO P03: authorized current source reads; VERIFIED/BLOCKED/UNKNOWN/NOT_APPLICABLE.
    not_implemented()


@router.put(
    "/hires/{hire_id}/sources/{source_id}",
    response_model=SourceRecord,
    summary="Record a typed simulated-system observation",
)
def write_source(hire_id: str, source_id: str, body: SourceWrite):
    # TODO P03: category/field authority, expected version, timestamp/audit and fresh check.
    not_implemented()
