"""The one server-side permission matrix. The AI has no row here: it can never approve."""

from app.shared.contracts import Role
from app.shared.errors import forbidden

ALL = frozenset(Role)
STAFF = frozenset(Role) - {Role.EMPLOYEE}

PERMISSIONS: dict[str, frozenset[Role]] = {
    "hire.create": frozenset({Role.HR}),
    "hire.edit": frozenset({Role.HR}),
    "hire.contact_fields": frozenset({Role.HR}),
    "reference.read": frozenset({Role.HR, Role.MANAGER, Role.IT}),
    "task.reassign": frozenset({Role.HR}),
    "document.upload": frozenset({Role.HR, Role.EMPLOYEE}),
    "document.queue": frozenset({Role.HR}),
    "document.extract": frozenset({Role.HR}),
    "document.review": frozenset({Role.HR}),
    "equipment.read": frozenset({Role.HR, Role.IT}),
    "equipment.request": frozenset({Role.IT, Role.MANAGER}),
    "access.request": frozenset({Role.IT, Role.MANAGER}),
    "checks.run": STAFF,
    "case.open": frozenset({Role.HR, Role.MANAGER}),
    "proposal.location": frozenset({Role.HR}),
    "knowledge.manage": frozenset({Role.HR}),
    "escalation.manage": frozenset({Role.HR}),
    "analytics.read": frozenset({Role.HR}),
    "insights.read": frozenset({Role.HR}),
    "audit.read": frozenset({Role.HR}),
    "metrics.read": frozenset({Role.HR}),
    "sweep.run": frozenset({Role.HR}),
}

# Who may write each simulated-system category, once the hire is in scope.
SOURCE_WRITERS: dict[str, frozenset[Role]] = {
    "equipment": frozenset({Role.IT}),
    "it_access": frozenset({Role.IT}),
    "payroll": frozenset({Role.PAYROLL}),
    "benefits": frozenset({Role.BENEFITS, Role.EMPLOYEE}),
    "training": frozenset({Role.TRAINING}),
    "manager": frozenset({Role.MANAGER}),
    "documents": frozenset(),  # Document state only changes through the review endpoint.
}

# Staff who only see their own part of a plan. HR, managers and the employee see all of it.
CATEGORY_VIEW: dict[Role, frozenset[str]] = {
    Role.IT: frozenset({"equipment", "it_access"}),
    Role.PAYROLL: frozenset({"payroll"}),
    Role.BENEFITS: frozenset({"benefits"}),
    Role.TRAINING: frozenset({"training"}),
}

# Knowledge levels are filtered in SQL before ranking, so a restricted passage cannot be retrieved.
KNOWLEDGE_ACCESS: dict[Role, tuple[str, ...]] = {
    Role.HR: ("GENERAL", "MANAGER", "IT", "PAYROLL", "BENEFITS", "HR"),
    Role.MANAGER: ("GENERAL", "MANAGER"),
    Role.IT: ("GENERAL", "IT"),
    Role.PAYROLL: ("GENERAL", "PAYROLL"),
    Role.BENEFITS: ("GENERAL", "BENEFITS"),
    Role.TRAINING: ("GENERAL",),
    Role.EMPLOYEE: ("GENERAL",),
}

# These document categories never leave the machine, whatever the model configuration says.
SENSITIVE_DOCUMENTS = frozenset({"government_id", "bank_details", "tax"})


def can(role: Role, permission: str) -> bool:
    return role in PERMISSIONS[permission]


def require(role: Role, permission: str) -> None:
    if role not in PERMISSIONS[permission]:
        forbidden()
