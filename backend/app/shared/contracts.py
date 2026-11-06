"""Frozen v1 wire contracts. Track 1 reviews all changes before other tracks consume them."""

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


Id = Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")]
ShortText = Annotated[str, Field(min_length=1, max_length=200)]
Location = Literal["HYD-DEMO", "BLR-DEMO"]


class Role(StrEnum):
    HR = "HR"
    IT = "IT"
    PAYROLL = "PAYROLL"
    BENEFITS = "BENEFITS"
    TRAINING = "TRAINING"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class Category(StrEnum):
    DOCUMENTS = "documents"
    EQUIPMENT = "equipment"
    PAYROLL = "payroll"
    BENEFITS = "benefits"
    TRAINING = "training"
    MANAGER = "manager"


class WorkState(StrEnum):
    PENDING = "PENDING"
    WAITING_DEPENDENCY = "WAITING_DEPENDENCY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CheckResult(StrEnum):
    VERIFIED = "VERIFIED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class CaseState(StrEnum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    WAITING_HUMAN = "WAITING_HUMAN"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class ErrorDetail(Contract):
    field: str
    message: str


class ErrorBody(Contract):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(Contract):
    error: ErrorBody


class Health(Contract):
    status: Literal["ok"] = "ok"
    database: Literal["ok"] = "ok"
    schema_version: Literal[1] = 1


class Bootstrap(Contract):
    project_name: str
    message: str
    foundation_only: Literal[True] = True


class LoginRequest(Contract):
    user_id: Id
    password: Annotated[str, Field(min_length=12, max_length=128)]


class User(Contract):
    id: Id
    display_name: ShortText
    role: Role
    hire_ids: list[Id]


class InvestigationContext(Contract):
    """Server-constructed run scope, never accepted from a browser/model."""

    user: User
    hire_id: Id
    case_id: Id


class Session(Contract):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_at: datetime
    user: User


class HireCreate(Contract):
    display_name: ShortText
    worker_type: Literal["employee", "contractor"]
    role: Literal["engineer", "operations_associate"]
    location_id: Location
    work_mode: Literal["office", "remote"]
    start_date: date
    manager_user_id: Id
    employee_user_id: Id | None = None


class Hire(HireCreate):
    id: Id
    profile_version: Annotated[int, Field(ge=1)]
    plan_version: Annotated[int, Field(ge=1)]


class HireList(Contract):
    items: list[Hire]


class Task(Contract):
    id: Id
    hire_id: Id
    category: Category
    title: ShortText
    owner_user_id: Id
    due_date: date
    critical: bool
    work_state: WorkState
    version: Annotated[int, Field(ge=1)]
    depends_on: list[Id]


class TaskList(Contract):
    items: list[Task]


class Evidence(Contract):
    id: Id
    hire_id: Id
    case_id: Id | None = None
    check_type: ShortText
    source_record_id: Id | None = None
    source_version: Annotated[int, Field(ge=1)] | None = None
    profile_version: Annotated[int, Field(ge=1)]
    policy_id: Id
    policy_version: Annotated[int, Field(ge=1)]
    checked_at: datetime
    expires_at: datetime | None = None
    result: CheckResult
    reason_code: ShortText
    # Observations are sanitized display facts, never an executable action payload.
    observed: dict[str, str | int | bool | None]


class EvidenceList(Contract):
    items: list[Evidence]


class ToolObservation(Contract):
    evidence: list[Evidence]
    facts: dict[str, str | int | bool | None]
    untrusted_text: Annotated[str, Field(max_length=12000)] | None = None


class ActionResult(Contract):
    action_id: Id
    state: Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "UNKNOWN"]
    observed: dict[str, str | int | bool | None]
    evidence: list[Evidence]


class Plan(Contract):
    hire_id: Id
    plan_version: Annotated[int, Field(ge=1)]
    tasks: list[Task]
    checks: list[Evidence]


class VersionRequest(Contract):
    expected_version: Annotated[int, Field(ge=1)]


class CaseCreate(Contract):
    message: Annotated[str, Field(min_length=1, max_length=2000)]


class WorkItem(Contract):
    id: Id
    case_id: Id
    kind: Literal["INVESTIGATE", "RESUME", "EXECUTE"]
    state: Literal["PENDING", "RUNNING", "DONE", "FAILED"]
    attempts: Annotated[int, Field(ge=0)]
    updated_at: datetime


class AcceptedWork(Contract):
    case_id: Id
    work_item_id: Id


class Question(Contract):
    id: Id
    case_id: Id
    recipient_user_id: Id
    text: Annotated[str, Field(min_length=1, max_length=1000)]
    state: Literal["PENDING", "ANSWERED", "CANCELLED"]
    answer: Annotated[str, Field(max_length=1000)] | None = None


class AnswerRequest(Contract):
    answer: Annotated[str, Field(min_length=1, max_length=1000)]


class ExpectedVersions(Contract):
    profile_version: Annotated[int, Field(ge=1)]
    plan_version: Annotated[int, Field(ge=1)]
    policy_id: Id
    policy_version: Annotated[int, Field(ge=1)]
    source_record_id: Id | None = None
    source_version: Annotated[int, Field(ge=1)] | None = None


class LocationAction(Contract):
    action_type: Literal["CHANGE_WORK_LOCATION"]
    location_id: Location


class ReservationAction(Contract):
    action_type: Literal["RESERVE_EQUIPMENT"]
    equipment_record_id: Id


ActionPayload = Annotated[LocationAction | ReservationAction, Field(discriminator="action_type")]


class PlanDiff(Contract):
    create: list[ShortText]
    cancel: list[Id]
    preserve: list[Id]
    invalidate_checks: list[Id]


class Proposal(Contract):
    id: Id
    case_id: Id
    payload: ActionPayload
    evidence_ids: list[Id]
    expected_versions: ExpectedVersions
    reviewer_role: Literal["HR", "IT"]
    expires_at: datetime
    plan_diff: PlanDiff | None = None


class ProposalList(Contract):
    items: list[Proposal]


class PreviewRequest(Contract):
    case_id: Id
    location_id: Location
    expected_profile_version: Annotated[int, Field(ge=1)]


class DecisionRequest(Contract):
    decision: Literal["APPROVE", "REJECT"]
    note: Annotated[str, Field(max_length=500)] = ""


class DecisionResult(Contract):
    proposal_id: Id
    decision: Literal["APPROVE", "REJECT"]
    action_id: Id | None = None
    work_item_id: Id | None = None


class AuditEvent(Contract):
    id: Id
    event_type: ShortText
    summary: Annotated[str, Field(max_length=500)]
    created_at: datetime


class Case(Contract):
    id: Id
    hire_id: Id
    state: CaseState
    version: Annotated[int, Field(ge=1)]
    model_calls: Annotated[int, Field(ge=0)]
    tool_calls: Annotated[int, Field(ge=0)]
    questions: list[Question]
    proposals: list[Proposal]
    evidence: list[Evidence]
    timeline: list[AuditEvent]


class DocumentInput(Contract):
    category: Literal["documents"]
    text: Annotated[str, Field(min_length=1, max_length=12000)]
    review_state: Literal["SUBMITTED", "REVIEWED"]


class EquipmentInput(Contract):
    category: Literal["equipment"]
    asset_tag: Id
    location_id: Location
    state: Literal["AVAILABLE", "RESERVED", "HANDED_OVER"]
    assignee_hire_id: Id | None = None
    handover_at: datetime | None = None


class PayrollInput(Contract):
    category: Literal["payroll"]
    profile_created: bool
    setup_confirmed: bool


class BenefitsInput(Contract):
    category: Literal["benefits"]
    state: Literal["NOT_INVITED", "INVITED", "ENROLLED", "DECLINED"]


class TrainingInput(Contract):
    category: Literal["training"]
    course_id: Id
    state: Literal["ASSIGNED", "COMPLETED"]


class ManagerInput(Contract):
    category: Literal["manager"]
    buddy_user_id: Id
    first_week_plan: Annotated[str, Field(min_length=1, max_length=2000)]


SourcePayload = Annotated[
    DocumentInput | EquipmentInput | PayrollInput | BenefitsInput | TrainingInput | ManagerInput,
    Field(discriminator="category"),
]


class SourceWrite(Contract):
    expected_version: Annotated[int, Field(ge=0)]
    payload: SourcePayload


class SourceRecord(Contract):
    id: Id
    hire_id: Id | None
    version: Annotated[int, Field(ge=1)]
    source_system: Literal["demo"] = "demo"
    observed_at: datetime
    payload: SourcePayload


class ReadStep(Contract):
    step: Literal["read"]
    tool: Literal[
        "get_hire_context",
        "get_onboarding_tasks",
        "get_document_evidence",
        "get_applicable_policy",
        "get_equipment_status",
        "get_payroll_setup_status",
        "get_task_outcome_evidence",
    ]
    reason_summary: ShortText


class AskStep(Contract):
    step: Literal["ask"]
    question: Annotated[str, Field(min_length=1, max_length=1000)]
    recipient_role: Role
    evidence_ids: list[Id]


class ProposeStep(Contract):
    step: Literal["propose"]
    payload: ActionPayload
    evidence_ids: Annotated[list[Id], Field(min_length=1)]
    reason_summary: ShortText


class FinishStep(Contract):
    step: Literal["finish", "escalate"]
    reason_summary: ShortText
    evidence_ids: list[Id]


class NextStep(Contract):
    next_step: Annotated[ReadStep | AskStep | ProposeStep | FinishStep, Field(discriminator="step")]


def utc_now() -> datetime:
    return datetime.now(UTC)
