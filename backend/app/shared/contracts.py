"""Wire contracts v2. Track 1 reviews all changes before other tracks consume them."""

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


Id = Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")]
ShortText = Annotated[str, Field(min_length=1, max_length=200)]
Location = Literal["HYD-DEMO", "BLR-DEMO"]
Observed = dict[str, str | int | bool | None]


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
    IT_ACCESS = "it_access"
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


class DisplayStatus(StrEnum):
    """Computed at read time, so OVERDUE and BLOCKED can never go stale in storage."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    OVERDUE = "OVERDUE"
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
    schema_version: Literal[2] = 2


class AiHealth(Contract):
    provider: str
    model: str
    available: bool
    is_stub: bool
    detail: str


class Bootstrap(Contract):
    project_name: str
    message: str
    foundation_only: Literal[False] = False


class LoginRequest(Contract):
    # An email address or a user ID. Either identifies the same account.
    user_id: Annotated[str, Field(min_length=1, max_length=200)]
    password: Annotated[str, Field(min_length=12, max_length=128)]


class AccountCreate(Contract):
    display_name: ShortText
    email: Annotated[str, Field(min_length=3, max_length=200)]
    password: Annotated[str, Field(min_length=12, max_length=128)]


class PasswordResetCreate(Contract):
    email: Annotated[str, Field(min_length=1, max_length=200)]


class PasswordReset(Contract):
    id: Id
    display_name: ShortText
    email: str | None = None
    role: str
    created_at: datetime


class PasswordResetList(Contract):
    items: list[PasswordReset]


class TemporaryPassword(Contract):
    display_name: ShortText
    temporary_password: str


class DemoPassword(Contract):
    """The shared password of the seeded synthetic demo accounts, for sign-in page autofill."""

    password: str


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


class Department(Contract):
    id: Id
    name: ShortText


class UserSummary(Contract):
    id: Id
    display_name: ShortText
    role: Role


class Reference(Contract):
    departments: list[Department]
    locations: list[Location]
    users: list[UserSummary]
    available_employee_user_ids: list[Id]


class HireCreate(Contract):
    display_name: ShortText
    worker_type: Literal["employee", "contractor"]
    role: Literal["engineer", "operations_associate", "sales_associate"]
    location_id: Location
    work_mode: Literal["office", "remote"]
    start_date: date
    manager_user_id: Id
    employee_user_id: Id | None = None
    department_id: Id
    designation: ShortText
    work_email: ShortText
    personal_email: ShortText | None = None
    phone: ShortText | None = None


class HirePatch(Contract):
    expected_profile_version: Annotated[int, Field(ge=1)]
    designation: ShortText | None = None
    work_email: ShortText | None = None
    personal_email: ShortText | None = None
    phone: ShortText | None = None
    department_id: Id | None = None
    employment_status: Literal["PRE_JOINING", "ACTIVE", "WITHDRAWN"] | None = None


class Hire(HireCreate):
    id: Id
    employee_code: ShortText
    employment_status: Literal["PRE_JOINING", "ACTIVE", "WITHDRAWN"]
    onboarding_status: Literal["NOT_STARTED", "IN_PROGRESS", "BLOCKED", "COMPLETED"]
    tasks_completed: Annotated[int, Field(ge=0)]
    tasks_total: Annotated[int, Field(ge=0)]
    tasks_overdue: Annotated[int, Field(ge=0)]
    created_at: datetime
    completed_at: datetime | None = None
    profile_version: Annotated[int, Field(ge=1)]
    plan_version: Annotated[int, Field(ge=1)]


class HireList(Contract):
    items: list[Hire]


class Task(Contract):
    id: Id
    hire_id: Id
    hire_name: ShortText
    category: Category
    title: ShortText
    description: str
    owner_user_id: Id
    owner_name: ShortText
    due_date: date
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    critical: bool
    work_state: WorkState
    display_status: DisplayStatus
    check_type: str | None = None
    evidence_result: CheckResult | None = None
    completed_at: datetime | None = None
    version: Annotated[int, Field(ge=1)]
    depends_on: list[Id]


class TaskList(Contract):
    items: list[Task]


class TaskReassign(Contract):
    expected_version: Annotated[int, Field(ge=1)]
    owner_user_id: Id


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
    observed: Observed


class EvidenceList(Contract):
    items: list[Evidence]


class ToolObservation(Contract):
    evidence: list[Evidence]
    facts: Observed
    untrusted_text: Annotated[str, Field(max_length=12000)] | None = None


class ActionResult(Contract):
    action_id: Id
    state: Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "UNKNOWN"]
    observed: Observed
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
    hire_name: str | None = None
    recipient_user_id: Id
    text: Annotated[str, Field(min_length=1, max_length=1000)]
    state: Literal["PENDING", "ANSWERED", "CANCELLED"]
    answer: Annotated[str, Field(max_length=1000)] | None = None


class QuestionList(Contract):
    items: list[Question]


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
    restore: list[Id] = Field(default_factory=list)
    invalidate_checks: list[Id]


class Proposal(Contract):
    id: Id
    case_id: Id
    hire_id: Id
    hire_name: ShortText
    payload: ActionPayload
    evidence_ids: list[Id]
    expected_versions: ExpectedVersions
    reviewer_role: Literal["HR", "IT"]
    expires_at: datetime
    plan_diff: PlanDiff | None = None
    decision: Literal["APPROVE", "REJECT"] | None = None
    action_state: Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "UNKNOWN"] | None = None
    outcome: str | None = None


class ProposalList(Contract):
    items: list[Proposal]


class PreviewRequest(Contract):
    case_id: Id | None = None
    location_id: Location
    expected_profile_version: Annotated[int, Field(ge=1)]


class EquipmentRequest(Contract):
    equipment_record_id: Id


class AccessRequest(Contract):
    item: Literal["CORPORATE_EMAIL", "VPN", "APPLICATION_ACCESS", "REQUIRED_SOFTWARE"]
    detail: Annotated[str, Field(max_length=200)] = ""


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
    hire_id: Id | None = None
    actor_user_id: Id | None = None
    event_type: ShortText
    summary: Annotated[str, Field(max_length=500)]
    created_at: datetime


class AuditEventList(Contract):
    items: list[AuditEvent]


class Case(Contract):
    id: Id
    hire_id: Id
    state: CaseState
    kind: Literal["INVESTIGATION", "MANUAL"]
    message: str
    version: Annotated[int, Field(ge=1)]
    model_calls: Annotated[int, Field(ge=0)]
    tool_calls: Annotated[int, Field(ge=0)]
    questions: list[Question]
    proposals: list[Proposal]
    evidence: list[Evidence]
    timeline: list[AuditEvent]


class CaseList(Contract):
    items: list[Case]


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
    asset_name: Annotated[str, Field(max_length=120)] = ""
    asset_type: Annotated[str, Field(max_length=60)] = ""
    serial_number: Annotated[str, Field(max_length=60)] = ""


class ItAccessInput(Contract):
    category: Literal["it_access"]
    item: Literal["CORPORATE_EMAIL", "VPN", "APPLICATION_ACCESS", "REQUIRED_SOFTWARE"]
    detail: Annotated[str, Field(max_length=200)] = ""
    state: Literal["REQUESTED", "PROVISIONED"]
    # Honest label: nothing real is provisioned in this prototype.
    simulated: Literal[True] = True


class PayrollInput(Contract):
    """Status only. Bank and tax numbers are deliberately not representable here."""

    category: Literal["payroll"]
    profile_created: bool
    setup_confirmed: bool
    bank_submitted: bool = False
    tax_submitted: bool = False


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
    DocumentInput
    | EquipmentInput
    | ItAccessInput
    | PayrollInput
    | BenefitsInput
    | TrainingInput
    | ManagerInput,
    Field(discriminator="category"),
]


class SourceWrite(Contract):
    expected_version: Annotated[int, Field(ge=0)]
    payload: SourcePayload


class SourceRecord(Contract):
    id: Id
    hire_id: Id | None
    hire_name: str | None = None
    version: Annotated[int, Field(ge=1)]
    source_system: Literal["demo"] = "demo"
    observed_at: datetime
    payload: SourcePayload


class SourceRecordList(Contract):
    items: list[SourceRecord]


DocumentCategory = Literal[
    "government_id",
    "address_proof",
    "education",
    "previous_employment",
    "bank_details",
    "tax",
    "signed_employment",
]
DocumentState = Literal[
    "SUBMITTED", "UNDER_REVIEW", "VERIFIED", "REJECTED", "RESUBMISSION_REQUESTED", "SUPERSEDED"
]


class DocumentReview(Contract):
    id: Id
    reviewer_user_id: Id
    decision: Literal["VERIFY", "REJECT", "REQUEST_RESUBMISSION"]
    reason: str
    created_at: datetime


class Document(Contract):
    id: Id
    hire_id: Id
    hire_name: ShortText
    category: DocumentCategory
    state: DocumentState
    original_name: ShortText
    mime_type: ShortText
    size_bytes: Annotated[int, Field(ge=1)]
    text_available: bool
    declared_location_id: Location | None = None
    version: Annotated[int, Field(ge=1)]
    created_at: datetime
    reviews: list[DocumentReview]


class DocumentList(Contract):
    items: list[Document]


class DocumentReviewRequest(Contract):
    decision: Literal["VERIFY", "REJECT", "REQUEST_RESUBMISSION"]
    reason: Annotated[str, Field(max_length=500)] = ""
    expected_version: Annotated[int, Field(ge=1)]


class ExtractedField(Contract):
    name: ShortText
    value: ShortText
    quote: Annotated[str, Field(min_length=1, max_length=300)]


class Mismatch(Contract):
    field: ShortText
    document_value: ShortText
    profile_value: ShortText


class DocumentExtractionOutput(Contract):
    """What the model may return. Comparison against the profile is done by code afterwards."""

    suggested_category: DocumentCategory
    fields: Annotated[list[ExtractedField], Field(max_length=12)]
    missing: Annotated[list[ShortText], Field(max_length=10)]
    summary: Annotated[str, Field(min_length=1, max_length=600)]


class DocumentExtraction(Contract):
    id: Id
    document_id: Id
    suggested_category: DocumentCategory
    fields: list[ExtractedField]
    missing: list[ShortText]
    mismatches: list[Mismatch]
    summary: str
    advisory: Literal[True] = True
    ai_run_id: Id
    model: str
    is_stub: bool
    created_at: datetime


class AssistantQuestion(Contract):
    question: Annotated[str, Field(min_length=3, max_length=500)]


class ModelCitation(Contract):
    chunk_id: Id
    quote: Annotated[str, Field(min_length=1, max_length=400)]


class ModelClaim(Contract):
    text: Annotated[str, Field(min_length=1, max_length=500)]
    citations: Annotated[list[ModelCitation], Field(min_length=1, max_length=4)]


class AssistantOutput(Contract):
    """Model output. The UI renders claims only, so an uncited sentence cannot be shown."""

    status: Literal["ANSWERED", "PARTIAL", "NOT_FOUND", "OUT_OF_SCOPE"]
    claims: Annotated[list[ModelClaim], Field(max_length=6)]
    uncertainty: Annotated[str, Field(max_length=400)] = ""
    suggest_escalation: bool = False


class Citation(Contract):
    chunk_id: Id
    document_id: Id
    title: ShortText
    version: Annotated[int, Field(ge=1)]
    section_ref: str
    access_level: str
    quote: str


class AssistantClaim(Contract):
    text: str
    citations: list[Citation]


class AssistantAnswer(Contract):
    status: Literal["ANSWERED", "PARTIAL", "NOT_FOUND", "OUT_OF_SCOPE", "UNAVAILABLE"]
    message: str
    claims: list[AssistantClaim]
    uncertainty: str
    suggest_escalation: bool
    sources: list[Citation]
    ai_run_id: Id
    model: str
    is_stub: bool


class EscalationCreate(Contract):
    question: Annotated[str, Field(min_length=3, max_length=500)]
    ai_run_id: Id | None = None


class Escalation(Contract):
    id: Id
    raised_by: Id
    raised_by_name: ShortText
    question: str
    state: Literal["OPEN", "ANSWERED"]
    resolution: str | None = None
    created_at: datetime


class EscalationList(Contract):
    items: list[Escalation]


class EscalationAnswer(Contract):
    answer: Annotated[str, Field(min_length=1, max_length=1000)]


class KnowledgeDocument(Contract):
    id: Id
    version: Annotated[int, Field(ge=1)]
    title: ShortText
    access_level: Literal["GENERAL", "MANAGER", "IT", "PAYROLL", "BENEFITS", "HR"]
    status: Literal["DRAFT", "APPROVED", "RETIRED"]
    chunk_count: Annotated[int, Field(ge=0)]
    created_at: datetime


class KnowledgeDocumentList(Contract):
    items: list[KnowledgeDocument]


class KnowledgeApprove(Contract):
    version: Annotated[int, Field(ge=1)]


class Notification(Contract):
    id: Id
    type: ShortText
    title: ShortText
    body: str
    hire_id: Id | None = None
    task_id: Id | None = None
    read: bool
    created_at: datetime


class NotificationList(Contract):
    items: list[Notification]
    unread: Annotated[int, Field(ge=0)]


class SweepResult(Contract):
    notifications_created: Annotated[int, Field(ge=0)]


class CountItem(Contract):
    label: str
    count: Annotated[int, Field(ge=0)]


class UpcomingJoiner(Contract):
    hire_id: Id
    display_name: ShortText
    start_date: date
    location_id: Location


class Overview(Contract):
    total_employees: Annotated[int, Field(ge=0)]
    onboarding_in_progress: Annotated[int, Field(ge=0)]
    onboarding_completed: Annotated[int, Field(ge=0)]
    tasks_pending: Annotated[int, Field(ge=0)]
    tasks_overdue: Annotated[int, Field(ge=0)]
    documents_awaiting: Annotated[int, Field(ge=0)]
    claims_without_proof: Annotated[int, Field(ge=0)]
    average_completion_days: float | None = None
    by_department: list[CountItem]
    by_location: list[CountItem]
    equipment: list[CountItem]
    upcoming: list[UpcomingJoiner]
    recent: list[AuditEvent]


class InsightEvidence(Contract):
    ref: Id
    label: str


class InsightMetric(Contract):
    id: Id
    label: str
    value: Annotated[int, Field(ge=0)]
    evidence: list[InsightEvidence]


class InsightMetrics(Contract):
    metrics: list[InsightMetric]


class ModelRecommendation(Contract):
    text: Annotated[str, Field(min_length=1, max_length=300)]
    evidence_refs: Annotated[list[Id], Field(min_length=1, max_length=6)]


class InsightOutput(Contract):
    summary: Annotated[str, Field(min_length=1, max_length=800)]
    recommendations: Annotated[list[ModelRecommendation], Field(max_length=5)]


class InsightSummary(InsightOutput):
    advisory: Literal[True] = True
    ai_run_id: Id
    model: str
    is_stub: bool
    metrics: list[InsightMetric]


class AiRun(Contract):
    id: Id
    operation: ShortText
    prompt_version: Annotated[int, Field(ge=1)]
    provider: str
    model: str
    user_id: Id | None = None
    hire_id: Id | None = None
    case_id: Id | None = None
    chunk_ids: list[Id]
    status: Literal["VALIDATED", "ABSTAINED", "REJECTED_OUTPUT", "UNAVAILABLE"]
    validation_result: str
    failure_reason: str | None = None
    attempts: Annotated[int, Field(ge=0)]
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: Annotated[int, Field(ge=0)]
    retrieval_ms: int | None = None
    created_at: datetime


class AiRunList(Contract):
    items: list[AiRun]


class OperationMetric(Contract):
    operation: str
    runs: Annotated[int, Field(ge=0)]
    validated: Annotated[int, Field(ge=0)]
    abstained: Annotated[int, Field(ge=0)]
    rejected: Annotated[int, Field(ge=0)]
    unavailable: Annotated[int, Field(ge=0)]
    average_latency_ms: float
    total_tokens: Annotated[int, Field(ge=0)]


class Metrics(Contract):
    api_requests: Annotated[int, Field(ge=0)]
    api_p50_ms: float
    api_p95_ms: float
    api_errors: Annotated[int, Field(ge=0)]
    retrieval_average_ms: float | None = None
    operations: list[OperationMetric]
    work_failed: Annotated[int, Field(ge=0)]
    actions_failed: Annotated[int, Field(ge=0)]
    task_completion_rate: float


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
