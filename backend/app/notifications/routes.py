from fastapi import APIRouter, Depends

from app.auth.permissions import require
from app.auth.service import require_user
from app.notifications import service
from app.shared.contracts import NotificationList, SweepResult, User
from app.shared.db import connect
from app.shared.errors import not_found
from app.shared.util import now_iso

router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=NotificationList, summary="Read my notifications")
def list_notifications(user: User = Depends(require_user)):
    with connect() as connection:
        return service.list_for_user(connection, user.id)


@router.post(
    "/notifications/{notification_id}/read", status_code=204, summary="Mark a notification read"
)
def mark_read(notification_id: str, user: User = Depends(require_user)):
    with connect() as connection:
        cursor = connection.execute(
            "UPDATE notifications SET read_at=COALESCE(read_at, ?) WHERE id=? AND user_id=?",
            (now_iso(), notification_id, user.id),
        )
        if cursor.rowcount != 1:
            not_found()


@router.post(
    "/notifications/sweep", response_model=SweepResult, summary="Run the deadline escalation sweep"
)
def sweep(user: User = Depends(require_user)):
    require(user.role, "sweep.run")
    with connect() as connection:
        return SweepResult(notifications_created=service.run_escalation_sweep(connection))
