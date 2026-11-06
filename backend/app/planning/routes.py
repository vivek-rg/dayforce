from fastapi import APIRouter, Depends

from app.auth.permissions import require
from app.auth.service import require_hire_scope, require_user
from app.planning import service
from app.shared.contracts import (
    AuditEvent,
    AuditEventList,
    Department,
    Hire,
    HireCreate,
    HireList,
    HirePatch,
    Plan,
    Reference,
    Task,
    TaskList,
    TaskReassign,
    User,
    UserSummary,
    VersionRequest,
)
from app.shared.db import connect
from app.shared.errors import fail, stale
from app.shared.util import audit

router = APIRouter(tags=["planning"])


@router.get("/reference", response_model=Reference, summary="Read form options for staff screens")
def reference(user: User = Depends(require_user)):
    require(user.role, "reference.read")
    with connect() as connection:
        departments = connection.execute("SELECT * FROM departments ORDER BY name").fetchall()
        users = connection.execute(
            "SELECT id, display_name, role FROM users WHERE active=1 ORDER BY role, display_name"
        ).fetchall()
        available = connection.execute(
            "SELECT u.id FROM users u LEFT JOIN hires h ON h.employee_user_id=u.id "
            "WHERE u.role='EMPLOYEE' AND u.active=1 AND h.id IS NULL ORDER BY u.id"
        ).fetchall()
    return Reference(
        departments=[Department(id=row["id"], name=row["name"]) for row in departments],
        locations=["HYD-DEMO", "BLR-DEMO"],
        users=[
            UserSummary(id=row["id"], display_name=row["display_name"], role=row["role"])
            for row in users
        ],
        available_employee_user_ids=[row["id"] for row in available],
    )


@router.get("/hires", response_model=HireList, summary="List authorized hires")
def list_hires(user: User = Depends(require_user)):
    with connect() as connection:
        rows = [
            connection.execute("SELECT * FROM hires WHERE id=?", (hire_id,)).fetchone()
            for hire_id in user.hire_ids
        ]
        items = [service.to_hire(connection, row, user) for row in rows if row]
    return HireList(items=sorted(items, key=lambda hire: hire.start_date))


@router.post(
    "/hires", response_model=Hire, status_code=201, summary="Create hire and approved plan"
)
def create_hire(body: HireCreate, user: User = Depends(require_user)):
    require(user.role, "hire.create")
    with connect() as connection:
        return service.create_hire(connection, body, user)


@router.get("/hires/{hire_id}", response_model=Hire, summary="Read authorized hire profile")
def get_hire(hire_id: str, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    with connect() as connection:
        return service.to_hire(connection, service.get_hire_row(connection, hire_id), user)


@router.patch("/hires/{hire_id}", response_model=Hire, summary="Edit profile fields")
def patch_hire(hire_id: str, body: HirePatch, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    require(user.role, "hire.edit")
    changes = body.model_dump(exclude_unset=True, exclude={"expected_profile_version"})
    with connect() as connection:
        if (
            "department_id" in changes
            and not connection.execute(
                "SELECT 1 FROM departments WHERE id=?", (changes["department_id"],)
            ).fetchone()
        ):
            fail(422, "VALIDATION_ERROR", "Unknown department.")
        if changes:
            assignments = ", ".join(f"{column}=?" for column in changes)
            cursor = connection.execute(
                f"UPDATE hires SET {assignments}, profile_version=profile_version+1 "
                "WHERE id=? AND profile_version=?",
                (*changes.values(), hire_id, body.expected_profile_version),
            )
            if cursor.rowcount != 1:
                stale()
            audit(connection, hire_id, "HIRE_EDITED", "Fields: " + ", ".join(changes), user.id)
        return service.to_hire(connection, service.get_hire_row(connection, hire_id), user)


@router.get(
    "/hires/{hire_id}/history", response_model=AuditEventList, summary="Read a hire's audit history"
)
def history(hire_id: str, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    with connect() as connection:
        rows = connection.execute(
            "SELECT * FROM audit_events WHERE hire_id=? ORDER BY created_at DESC, rowid DESC "
            "LIMIT 100",
            (hire_id,),
        ).fetchall()
    return AuditEventList(
        items=[
            AuditEvent(
                id=row["id"],
                hire_id=row["hire_id"],
                actor_user_id=row["actor_user_id"],
                event_type=row["event_type"],
                summary=row["summary"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
    )


@router.get("/hires/{hire_id}/plan", response_model=Plan, summary="Read tasks and current evidence")
def get_plan(hire_id: str, user: User = Depends(require_user)):
    require_hire_scope(user, hire_id)
    with connect() as connection:
        return service.get_plan(connection, hire_id, user)


@router.get("/my-work", response_model=TaskList, summary="List current user-owned tasks")
def my_work(user: User = Depends(require_user)):
    with connect() as connection:
        return TaskList(items=service.my_work(connection, user))


@router.post("/tasks/{task_id}/start", response_model=Task, summary="Start an owned task")
def start_task(task_id: str, body: VersionRequest, user: User = Depends(require_user)):
    with connect() as connection:
        return service.start_task(connection, task_id, user, body.expected_version)


@router.post(
    "/tasks/{task_id}/complete", response_model=Task, summary="Record task completion claim"
)
def complete_task(task_id: str, body: VersionRequest, user: User = Depends(require_user)):
    with connect() as connection:
        return service.complete_task(connection, task_id, user, body.expected_version)


@router.post("/tasks/{task_id}/reassign", response_model=Task, summary="Reassign a task")
def reassign_task(task_id: str, body: TaskReassign, user: User = Depends(require_user)):
    require(user.role, "task.reassign")
    with connect() as connection:
        return service.reassign_task(
            connection, task_id, user, body.expected_version, body.owner_user_id
        )
