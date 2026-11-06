from fastapi import APIRouter

from app.shared.contracts import Hire, HireCreate, HireList, Plan, Task, TaskList, VersionRequest
from app.shared.errors import not_implemented

router = APIRouter(tags=["planning"])


@router.get("/hires", response_model=HireList, summary="List authorized hires")
def list_hires():
    # TODO P03: scope every row; return {items: []} when none are authorized.
    not_implemented()


@router.post(
    "/hires", response_model=Hire, status_code=201, summary="Create hire and approved plan"
)
def create_hire(body: HireCreate):
    # TODO P03: HR only; validate approved pack/owners; one transaction, no LLM.
    not_implemented()


@router.get("/hires/{hire_id}", response_model=Hire, summary="Read authorized hire profile")
def get_hire(hire_id: str):
    # TODO P03: use auth service before fetching/returning the profile.
    not_implemented()


@router.get("/hires/{hire_id}/plan", response_model=Plan, summary="Read tasks and current evidence")
def get_plan(hire_id: str):
    # TODO P03: compute currentness; old evidence remains history, never current green.
    not_implemented()


@router.get("/my-work", response_model=TaskList, summary="List current user-owned tasks")
def my_work():
    # TODO P03: owner and hire scope filtering; prerequisite-aware task states.
    not_implemented()


@router.post(
    "/tasks/{task_id}/complete", response_model=Task, summary="Record task completion claim"
)
def complete_task(task_id: str, body: VersionRequest):
    # TODO P03: owner + prerequisites + expected version; do not edit source/evidence.
    not_implemented()
