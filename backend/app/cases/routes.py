from fastapi import APIRouter

from app.shared.contracts import AcceptedWork, AnswerRequest, Case, CaseCreate, WorkItem
from app.shared.errors import not_implemented

router = APIRouter(tags=["cases"])


@router.post(
    "/hires/{hire_id}/cases",
    response_model=AcceptedWork,
    status_code=202,
    summary="Open or link investigation and queue work",
)
def create_case(hire_id: str, body: CaseCreate):
    # TODO P04: authorized hire; link one active case; durable unique event/work item.
    not_implemented()


@router.get(
    "/cases/{case_id}", response_model=Case, summary="Read scoped case and sanitized timeline"
)
def get_case(case_id: str):
    # TODO P04: authorization before checkpoint/evidence/transcript access.
    not_implemented()


@router.post(
    "/questions/{question_id}/responses",
    response_model=AcceptedWork,
    status_code=202,
    summary="Answer intended question and queue resume",
)
def answer_question(question_id: str, body: AnswerRequest):
    # TODO P04: recipient identity, question/case state; dedupe; answer is not approval.
    not_implemented()


@router.get(
    "/work-items/{work_item_id}", response_model=WorkItem, summary="Poll scoped durable work"
)
def get_work_item(work_item_id: str):
    # TODO P04: scope through case; no public raw error/traceback.
    not_implemented()
