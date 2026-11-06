"""Deterministic onboarding plans. Approved rules decide tasks, owners, dates and dependencies."""

import json
import sqlite3
from datetime import date, timedelta

from app.auth.permissions import CATEGORY_VIEW
from app.evidence.service import check_hire, latest_evidence
from app.notifications.service import notify, notify_role
from app.shared.contracts import (
    CheckResult,
    DisplayStatus,
    Hire,
    HireCreate,
    Location,
    Plan,
    PlanDiff,
    Role,
    Task,
    User,
    WorkState,
)
from app.shared.errors import fail, forbidden, invalid_state, not_found, stale
from app.shared.util import audit, new_id, now_iso, today


def review_required(message: str):
    fail(409, "POLICY_REVIEW_REQUIRED", message)


def rule_applies(rule: dict, hire: dict) -> bool:
    return all(
        hire.get(key) == value or (isinstance(value, list) and hire.get(key) in value)
        for key, value in rule.get("when", {}).items()
    )


def validate_rules(rules: list[dict]) -> None:
    """Reject packs with duplicate IDs or dependency cycles before any task is created."""
    ids = [rule["id"] for rule in rules]
    if len(ids) != len(set(ids)):
        review_required("Approved pack has duplicate rule IDs.")
    known = set(ids)
    remaining = {rule["id"]: set(rule.get("depends_on", [])) & known for rule in rules}
    while remaining:
        ready = [rule_id for rule_id, deps in remaining.items() if not deps]
        if not ready:
            review_required("Approved pack has a dependency cycle.")
        for rule_id in ready:
            del remaining[rule_id]
        for deps in remaining.values():
            deps.difference_update(ready)


def select_policy(connection: sqlite3.Connection, hire: dict, on_date: date):
    rows = connection.execute(
        "SELECT * FROM policies WHERE effective_from<=? "
        "AND (effective_to IS NULL OR effective_to>=?) ORDER BY id, version DESC",
        (on_date.isoformat(), on_date.isoformat()),
    ).fetchall()
    for row in rows:
        scope = json.loads(row["scope_json"])
        if (
            hire["location_id"] in scope["locations"]
            and hire["worker_type"] in scope["worker_types"]
            and hire["role"] in scope["roles"]
        ):
            return row
    review_required("No approved onboarding policy covers this profile. HR must review manually.")


def applicable_rules(policy, hire: dict) -> list[dict]:
    rules = [rule for rule in json.loads(policy["rules_json"]) if rule_applies(rule, hire)]
    if not rules:
        review_required("The approved policy has no rule for this profile.")
    validate_rules(rules)
    return rules


def resolve_owner(connection: sqlite3.Connection, rule: dict, hire: dict, fallback: str) -> str:
    role = rule["owner_role"]
    if role == "MANAGER":
        return hire["manager_user_id"]
    if role == "EMPLOYEE":
        return hire.get("employee_user_id") or fallback
    row = connection.execute(
        "SELECT id FROM users WHERE role=? AND active=1 ORDER BY id LIMIT 1", (role,)
    ).fetchone()
    if row is None:
        review_required(f"No active {role} user can own rule {rule['id']}.")
    return row["id"]


def due_date_for(start_date: date, rule: dict) -> date:
    return start_date - timedelta(days=rule["due_calendar_days_before_start"])


def display_status(
    work_state: str, evidence: str | None, pending_approval: bool, due: date, on_date: date
) -> DisplayStatus:
    """Pure mapping from stored facts to what people see. First matching line wins."""
    if work_state == WorkState.CANCELLED:
        return DisplayStatus.CANCELLED
    if work_state == WorkState.COMPLETED:
        return DisplayStatus.COMPLETED
    if pending_approval:
        return DisplayStatus.PENDING_APPROVAL
    if work_state == WorkState.WAITING_DEPENDENCY or evidence == CheckResult.BLOCKED:
        return DisplayStatus.BLOCKED
    if on_date > due:
        return DisplayStatus.OVERDUE
    if work_state == WorkState.IN_PROGRESS:
        return DisplayStatus.IN_PROGRESS
    return DisplayStatus.NOT_STARTED


def _pending_categories(connection, hire_id: str) -> set[str]:
    pending = set()
    if connection.execute(
        "SELECT 1 FROM documents WHERE hire_id=? AND state IN ('SUBMITTED','UNDER_REVIEW') LIMIT 1",
        (hire_id,),
    ).fetchone():
        pending.add("documents")
    if connection.execute(
        "SELECT 1 FROM proposals p JOIN cases c ON c.id=p.case_id "
        "LEFT JOIN decisions d ON d.proposal_id=p.id "
        "WHERE c.hire_id=? AND p.action_type='RESERVE_EQUIPMENT' AND d.proposal_id IS NULL "
        "AND p.expires_at>? LIMIT 1",
        (hire_id, now_iso()),
    ).fetchone():
        pending.add("equipment")
    return pending


def load_tasks(
    connection: sqlite3.Connection, hire_id: str, categories: frozenset[str] | None = None
) -> list[Task]:
    rows = connection.execute(
        "SELECT t.*, h.display_name AS hire_name, u.display_name AS owner_name FROM tasks t "
        "JOIN hires h ON h.id=t.hire_id JOIN users u ON u.id=t.owner_user_id "
        "WHERE t.hire_id=? ORDER BY t.due_date, t.logical_key",
        (hire_id,),
    ).fetchall()
    evidence = {item.check_type: item.result for item in latest_evidence(connection, hire_id)}
    pending = _pending_categories(connection, hire_id)
    dependencies: dict[str, list[str]] = {}
    for row in connection.execute(
        "SELECT d.task_id, d.prerequisite_task_id FROM task_dependencies d "
        "JOIN tasks t ON t.id=d.task_id WHERE t.hire_id=?",
        (hire_id,),
    ):
        dependencies.setdefault(row["task_id"], []).append(row["prerequisite_task_id"])
    current = today()
    tasks = []
    for row in rows:
        if categories is not None and row["category"] not in categories:
            continue
        result = evidence.get(row["check_type"])
        due = date.fromisoformat(row["due_date"])
        tasks.append(
            Task(
                id=row["id"],
                hire_id=row["hire_id"],
                hire_name=row["hire_name"],
                category=row["category"],
                title=row["title"],
                description=row["description"],
                owner_user_id=row["owner_user_id"],
                owner_name=row["owner_name"],
                due_date=due,
                priority=row["priority"],
                critical=bool(row["critical"]),
                work_state=row["work_state"],
                display_status=display_status(
                    row["work_state"], result, row["category"] in pending, due, current
                ),
                check_type=row["check_type"],
                evidence_result=result,
                completed_at=row["completed_at"],
                version=row["version"],
                depends_on=dependencies.get(row["id"], []),
            )
        )
    return tasks


def onboarding_status(tasks: list[Task]) -> str:
    live = [task for task in tasks if task.work_state != WorkState.CANCELLED]
    critical = [task for task in live if task.critical]
    if critical and all(
        task.work_state == WorkState.COMPLETED
        and task.evidence_result in (None, CheckResult.VERIFIED, CheckResult.NOT_APPLICABLE)
        for task in critical
    ):
        return "COMPLETED"
    if any(task.evidence_result == CheckResult.BLOCKED for task in live):
        return "BLOCKED"
    if any(task.work_state in (WorkState.COMPLETED, WorkState.IN_PROGRESS) for task in live):
        return "IN_PROGRESS"
    return "NOT_STARTED"


def to_hire(connection: sqlite3.Connection, row, viewer: User | None = None) -> Hire:
    tasks = load_tasks(connection, row["id"])
    live = [task for task in tasks if task.work_state != WorkState.CANCELLED]
    private = viewer is None or viewer.role == Role.HR or viewer.id == row["employee_user_id"]
    return Hire(
        id=row["id"],
        employee_code=row["employee_code"],
        display_name=row["display_name"],
        worker_type=row["worker_type"],
        role=row["role"],
        location_id=row["location_id"],
        work_mode=row["work_mode"],
        start_date=row["start_date"],
        manager_user_id=row["manager_user_id"],
        employee_user_id=row["employee_user_id"],
        department_id=row["department_id"],
        designation=row["designation"],
        work_email=row["work_email"],
        personal_email=row["personal_email"] if private else None,
        phone=row["phone"] if private else None,
        employment_status=row["employment_status"],
        onboarding_status=onboarding_status(tasks),
        tasks_completed=sum(task.work_state == WorkState.COMPLETED for task in live),
        tasks_total=len(live),
        tasks_overdue=sum(task.display_status == DisplayStatus.OVERDUE for task in live),
        created_at=row["created_at"],
        completed_at=row["completed_at"],
        profile_version=row["profile_version"],
        plan_version=row["plan_version"],
    )


def _initial_sources(connection, hire: dict, rule: dict, actor: str) -> None:
    source = rule.get("creates_source")
    if not source:
        return
    source_id = f"{source['category']}_{hire['id']}_{source.get('key', 'main')}"
    connection.execute(
        "INSERT OR IGNORE INTO source_records (id, hire_id, category, source_system, external_id, "
        "version, payload_json, observed_at, updated_by) VALUES (?,?,?,?,?,1,?,?,?)",
        (
            source_id,
            hire["id"],
            source["category"],
            "demo",
            source_id,
            json.dumps(source["payload"]),
            now_iso(),
            actor,
        ),
    )


def _insert_tasks(
    connection, hire: dict, policy, rules: list[dict], actor: str, skip_keys: set[str] = frozenset()
) -> None:
    keys = {rule["id"]: new_id("TSK") for rule in rules if rule["id"] not in skip_keys}
    existing = {
        row["logical_key"]: row["id"]
        for row in connection.execute(
            "SELECT id, logical_key FROM tasks WHERE hire_id=?", (hire["id"],)
        )
    }
    start = date.fromisoformat(str(hire["start_date"]))
    for rule in rules:
        if rule["id"] in skip_keys:
            continue
        owner = resolve_owner(connection, rule, hire, actor)
        connection.execute(
            "INSERT INTO tasks (id, hire_id, logical_key, category, title, description, "
            "owner_user_id, policy_id, policy_version, rule_id, check_type, due_date, priority, "
            "critical, work_state) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                keys[rule["id"]],
                hire["id"],
                rule["id"],
                rule["category"],
                rule["title"],
                rule.get("description", ""),
                owner,
                policy["id"],
                policy["version"],
                rule["id"],
                rule.get("required_check"),
                due_date_for(start, rule).isoformat(),
                rule.get("priority", "MEDIUM"),
                int(rule.get("critical", False)),
                WorkState.PENDING,
            ),
        )
        _initial_sources(connection, hire, rule, actor)
        connection.execute(
            "INSERT OR IGNORE INTO user_scopes (user_id, hire_id) VALUES (?,?)",
            (owner, hire["id"]),
        )
        notify(
            connection,
            owner,
            "TASK_ASSIGNED",
            "New task assigned",
            f"{rule['title']} for {hire['display_name']}",
            f"assigned:{keys[rule['id']]}",
            hire_id=hire["id"],
            task_id=keys[rule["id"]],
        )
    for rule in rules:
        if rule["id"] in skip_keys:
            continue
        for dep in rule.get("depends_on", []):
            prerequisite = keys.get(dep) or existing.get(dep)
            if prerequisite:
                connection.execute(
                    "INSERT OR IGNORE INTO task_dependencies VALUES (?,?)",
                    (keys[rule["id"]], prerequisite),
                )
    refresh_dependency_states(connection, hire["id"])


def refresh_dependency_states(connection: sqlite3.Connection, hire_id: str) -> None:
    """Tasks wait on open prerequisites and are released, and notified, when they clear."""
    for task in connection.execute(
        "SELECT id, title, owner_user_id, work_state FROM tasks WHERE hire_id=? "
        "AND work_state IN ('PENDING','WAITING_DEPENDENCY')",
        (hire_id,),
    ).fetchall():
        blocked = connection.execute(
            "SELECT 1 FROM task_dependencies d JOIN tasks p ON p.id=d.prerequisite_task_id "
            "WHERE d.task_id=? AND p.work_state NOT IN ('COMPLETED','CANCELLED') LIMIT 1",
            (task["id"],),
        ).fetchone()
        wanted = WorkState.WAITING_DEPENDENCY if blocked else WorkState.PENDING
        if task["work_state"] != wanted:
            connection.execute(
                "UPDATE tasks SET work_state=?, version=version+1 WHERE id=?",
                (wanted, task["id"]),
            )
            if wanted == WorkState.PENDING:
                notify(
                    connection,
                    task["owner_user_id"],
                    "TASK_UNBLOCKED",
                    "Task ready to start",
                    task["title"],
                    f"ready:{task['id']}",
                    hire_id=hire_id,
                    task_id=task["id"],
                )


def create_hire(connection: sqlite3.Connection, body: HireCreate, actor: User) -> Hire:
    manager = connection.execute(
        "SELECT role FROM users WHERE id=? AND active=1", (body.manager_user_id,)
    ).fetchone()
    if manager is None or manager["role"] != Role.MANAGER:
        fail(422, "VALIDATION_ERROR", "Assigned manager must be an active manager account.")
    if body.employee_user_id:
        employee = connection.execute(
            "SELECT role FROM users WHERE id=? AND active=1", (body.employee_user_id,)
        ).fetchone()
        if employee is None or employee["role"] != Role.EMPLOYEE:
            fail(422, "VALIDATION_ERROR", "Employee login must be an active employee account.")
        if connection.execute(
            "SELECT 1 FROM hires WHERE employee_user_id=?", (body.employee_user_id,)
        ).fetchone():
            fail(409, "INVALID_STATE", "That employee login already belongs to another hire.")
    if not connection.execute(
        "SELECT 1 FROM departments WHERE id=?", (body.department_id,)
    ).fetchone():
        fail(422, "VALIDATION_ERROR", "Unknown department.")
    hire = body.model_dump(mode="json")
    policy = select_policy(connection, hire, body.start_date)
    rules = applicable_rules(policy, hire)
    hire_id = new_id("HIRE")
    count = connection.execute("SELECT COUNT(*) AS n FROM hires").fetchone()["n"]
    hire["id"] = hire_id
    connection.execute(
        "INSERT INTO hires (id, employee_code, display_name, worker_type, role, location_id, "
        "work_mode, start_date, manager_user_id, employee_user_id, department_id, designation, "
        "work_email, personal_email, phone, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            hire_id,
            f"EMP-{1001 + count}",
            body.display_name,
            body.worker_type,
            body.role,
            body.location_id,
            body.work_mode,
            body.start_date.isoformat(),
            body.manager_user_id,
            body.employee_user_id,
            body.department_id,
            body.designation,
            body.work_email,
            body.personal_email,
            body.phone,
            now_iso(),
        ),
    )
    for user_id in {actor.id, body.manager_user_id, body.employee_user_id} - {None}:
        connection.execute("INSERT INTO user_scopes VALUES (?,?)", (user_id, hire_id))
    _insert_tasks(connection, hire, policy, rules, actor.id)
    check_hire(connection, hire_id)
    audit(
        connection,
        hire_id,
        "HIRE_CREATED",
        f"Plan generated from {policy['id']} v{policy['version']} with {len(rules)} tasks.",
        actor.id,
    )
    return to_hire(connection, get_hire_row(connection, hire_id), actor)


def get_hire_row(connection: sqlite3.Connection, hire_id: str):
    row = connection.execute("SELECT * FROM hires WHERE id=?", (hire_id,)).fetchone()
    if row is None:
        not_found()
    return row


def visible_categories(user: User, hire_row) -> frozenset[str] | None:
    return CATEGORY_VIEW.get(user.role)


def get_plan(connection: sqlite3.Connection, hire_id: str, user: User) -> Plan:
    row = get_hire_row(connection, hire_id)
    categories = visible_categories(user, row)
    tasks = load_tasks(connection, hire_id, categories)
    visible_checks = {task.check_type for task in tasks if task.check_type}
    checks = [e for e in latest_evidence(connection, hire_id) if e.check_type in visible_checks]
    return Plan(hire_id=hire_id, plan_version=row["plan_version"], tasks=tasks, checks=checks)


def my_work(connection: sqlite3.Connection, user: User) -> list[Task]:
    tasks: list[Task] = []
    for hire_id in user.hire_ids:
        tasks += [
            task
            for task in load_tasks(connection, hire_id)
            if task.owner_user_id == user.id and task.work_state != WorkState.CANCELLED
        ]
    return sorted(tasks, key=lambda task: (task.due_date, task.title))


def _owned_task(connection, task_id: str, user: User, expected: int):
    task = connection.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if task is None or task["hire_id"] not in user.hire_ids:
        not_found()
    if task["owner_user_id"] != user.id:
        forbidden()
    if task["version"] != expected:
        stale()
    return task


def _single_task(connection, task_id: str, user: User) -> Task:
    task = connection.execute("SELECT hire_id FROM tasks WHERE id=?", (task_id,)).fetchone()
    return next(item for item in load_tasks(connection, task["hire_id"]) if item.id == task_id)


def start_task(connection: sqlite3.Connection, task_id: str, user: User, expected: int) -> Task:
    task = _owned_task(connection, task_id, user, expected)
    if task["work_state"] != WorkState.PENDING:
        invalid_state("Only a ready task can be started.")
    cursor = connection.execute(
        "UPDATE tasks SET work_state='IN_PROGRESS', version=version+1 WHERE id=? AND version=?",
        (task_id, expected),
    )
    if cursor.rowcount != 1:
        stale()
    audit(connection, task["hire_id"], "TASK_STARTED", task["title"], user.id)
    return _single_task(connection, task_id, user)


def complete_task(connection: sqlite3.Connection, task_id: str, user: User, expected: int) -> Task:
    """Records a claim only. It never edits a source record or an evidence receipt."""
    task = _owned_task(connection, task_id, user, expected)
    if task["work_state"] not in (WorkState.PENDING, WorkState.IN_PROGRESS):
        invalid_state("This task cannot be completed from its current state.")
    cursor = connection.execute(
        "UPDATE tasks SET work_state='COMPLETED', completed_at=?, version=version+1 "
        "WHERE id=? AND version=?",
        (now_iso(), task_id, expected),
    )
    if cursor.rowcount != 1:
        stale()
    audit(connection, task["hire_id"], "TASK_COMPLETED", f"Claimed: {task['title']}", user.id)
    refresh_dependency_states(connection, task["hire_id"])
    check_hire(connection, task["hire_id"])
    refresh_completion(connection, task["hire_id"])
    return _single_task(connection, task_id, user)


def reassign_task(
    connection: sqlite3.Connection, task_id: str, user: User, expected: int, owner_id: str
) -> Task:
    task = connection.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if task is None or task["hire_id"] not in user.hire_ids:
        not_found()
    if task["version"] != expected:
        stale()
    if task["work_state"] in (WorkState.COMPLETED, WorkState.CANCELLED):
        invalid_state("A finished task cannot be reassigned.")
    owner = connection.execute(
        "SELECT id FROM users WHERE id=? AND active=1", (owner_id,)
    ).fetchone()
    if owner is None:
        fail(422, "VALIDATION_ERROR", "Unknown or inactive user.")
    connection.execute(
        "UPDATE tasks SET owner_user_id=?, version=version+1 WHERE id=? AND version=?",
        (owner_id, task_id, expected),
    )
    connection.execute(
        "INSERT OR IGNORE INTO user_scopes VALUES (?,?)", (owner_id, task["hire_id"])
    )
    notify(
        connection,
        owner_id,
        "TASK_ASSIGNED",
        "Task reassigned to you",
        task["title"],
        f"reassigned:{task_id}:{expected}",
        hire_id=task["hire_id"],
        task_id=task_id,
    )
    audit(connection, task["hire_id"], "TASK_REASSIGNED", task["title"], user.id)
    return _single_task(connection, task_id, user)


def refresh_completion(connection: sqlite3.Connection, hire_id: str) -> None:
    row = get_hire_row(connection, hire_id)
    finished = onboarding_status(load_tasks(connection, hire_id)) == "COMPLETED"
    if finished and row["completed_at"] is None:
        connection.execute(
            "UPDATE hires SET completed_at=?, employment_status='ACTIVE' WHERE id=?",
            (now_iso(), hire_id),
        )
        audit(connection, hire_id, "ONBOARDING_COMPLETED", "All critical work has proof.")
        body = f"{row['display_name']} has finished onboarding."
        notify_role(
            connection,
            "HR",
            hire_id,
            kind="ONBOARDING_COMPLETE",
            title="Onboarding complete",
            body=body,
            dedupe_key=f"complete:{hire_id}",
        )
        if row["employee_user_id"]:
            notify(
                connection,
                row["employee_user_id"],
                "ONBOARDING_COMPLETE",
                "Onboarding complete",
                "Everything is done. Welcome aboard.",
                f"complete:{hire_id}",
                hire_id=hire_id,
            )
    elif not finished and row["completed_at"] is not None:
        connection.execute("UPDATE hires SET completed_at=NULL WHERE id=?", (hire_id,))


def preview_location_change(
    connection: sqlite3.Connection, hire_id: str, location_id: Location
) -> PlanDiff:
    """Exact impact of a location change. Pure: nothing is written."""
    row = get_hire_row(connection, hire_id)
    hire = dict(row)
    hire["location_id"] = location_id
    existing = connection.execute(
        "SELECT id, logical_key, policy_id, policy_version, work_state FROM tasks WHERE hire_id=?",
        (hire_id,),
    ).fetchall()
    policy = select_policy(connection, hire, date.fromisoformat(row["start_date"]))
    rules = applicable_rules(policy, hire)
    wanted = {rule["id"]: rule for rule in rules}
    existing_keys = {task["logical_key"] for task in existing}
    cancel, preserve = [], []
    for task in existing:
        if task["logical_key"] in wanted or task["work_state"] == WorkState.COMPLETED:
            preserve.append(task["id"])
        elif task["work_state"] != WorkState.CANCELLED:
            cancel.append(task["id"])
    invalidated = [
        item.id
        for item in latest_evidence(connection, hire_id)
        if item.check_type in ("device_handover_recorded", "profile_location_confirmed")
    ]
    return PlanDiff(
        create=[rule["title"] for key, rule in wanted.items() if key not in existing_keys],
        cancel=cancel,
        preserve=preserve,
        invalidate_checks=invalidated,
    )


def apply_location_change(
    connection: sqlite3.Connection, hire_id: str, location_id: Location, actor: str
) -> None:
    """Called only by the approved-action executor, inside its transaction."""
    row = get_hire_row(connection, hire_id)
    hire = dict(row)
    hire["location_id"] = location_id
    policy = select_policy(connection, hire, date.fromisoformat(row["start_date"]))
    rules = applicable_rules(policy, hire)
    wanted = {rule["id"] for rule in rules}
    existing = connection.execute(
        "SELECT id, logical_key, work_state FROM tasks WHERE hire_id=?", (hire_id,)
    ).fetchall()
    for task in existing:
        if task["logical_key"] not in wanted and task["work_state"] not in (
            WorkState.COMPLETED,
            WorkState.CANCELLED,
        ):
            connection.execute(
                "UPDATE tasks SET work_state='CANCELLED', version=version+1 WHERE id=?",
                (task["id"],),
            )
    connection.execute(
        "UPDATE hires SET location_id=?, profile_version=profile_version+1, "
        "plan_version=plan_version+1 WHERE id=?",
        (location_id, hire_id),
    )
    _insert_tasks(
        connection, hire, policy, rules, actor, skip_keys={t["logical_key"] for t in existing}
    )
    refresh_dependency_states(connection, hire_id)
