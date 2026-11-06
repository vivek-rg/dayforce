"""In-app notifications behind a small adapter, plus the deterministic escalation sweep."""

import sqlite3
from datetime import date, timedelta
from typing import Protocol

from app.shared.contracts import Notification, NotificationList
from app.shared.util import new_id, now_iso, today


class NotificationAdapter(Protocol):
    """Email or chat delivery would implement this. Only in-app delivery exists today."""

    def deliver(self, connection: sqlite3.Connection, message: dict) -> bool: ...


class InAppAdapter:
    def deliver(self, connection: sqlite3.Connection, message: dict) -> bool:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO notifications "
            "(id, user_id, hire_id, task_id, type, title, body, dedupe_key, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                new_id("NTF"),
                message["user_id"],
                message.get("hire_id"),
                message.get("task_id"),
                message["type"],
                message["title"][:200],
                message["body"][:500],
                message["dedupe_key"],
                now_iso(),
            ),
        )
        return cursor.rowcount == 1


ADAPTERS: list[NotificationAdapter] = [InAppAdapter()]


def notify(
    connection: sqlite3.Connection,
    user_id: str,
    kind: str,
    title: str,
    body: str,
    dedupe_key: str,
    hire_id: str | None = None,
    task_id: str | None = None,
) -> bool:
    message = {
        "user_id": user_id,
        "type": kind,
        "title": title,
        "body": body,
        "dedupe_key": dedupe_key,
        "hire_id": hire_id,
        "task_id": task_id,
    }
    return any([adapter.deliver(connection, message) for adapter in ADAPTERS])


def notify_role(connection: sqlite3.Connection, role: str, hire_id: str | None, **kwargs) -> None:
    """Tell active users of a role, restricted to those who can already see this hire."""
    if hire_id:
        rows = connection.execute(
            "SELECT u.id FROM users u JOIN user_scopes s ON s.user_id=u.id "
            "WHERE u.role=? AND u.active=1 AND s.hire_id=?",
            (role, hire_id),
        ).fetchall()
    else:
        rows = connection.execute(
            "SELECT id FROM users WHERE role=? AND active=1", (role,)
        ).fetchall()
    for row in rows:
        notify(connection, row["id"], hire_id=hire_id, **kwargs)


def list_for_user(connection: sqlite3.Connection, user_id: str, limit: int = 50):
    rows = connection.execute(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC, id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    unread = connection.execute(
        "SELECT COUNT(*) AS n FROM notifications WHERE user_id=? AND read_at IS NULL", (user_id,)
    ).fetchone()["n"]
    return NotificationList(
        items=[
            Notification(
                id=row["id"],
                type=row["type"],
                title=row["title"],
                body=row["body"],
                hire_id=row["hire_id"],
                task_id=row["task_id"],
                read=row["read_at"] is not None,
                created_at=row["created_at"],
            )
            for row in rows
        ],
        unread=unread,
    )


def run_escalation_sweep(connection: sqlite3.Connection, on_date: date | None = None) -> int:
    """Ladder: 2 days before due, owner; overdue, owner; +1 day, manager; +2 or critical, HR.

    Deduped per task, level and day, so repeating the sweep cannot spam anyone.
    """
    current = on_date or today()
    created = 0
    rows = connection.execute(
        "SELECT t.*, h.display_name AS hire_name, h.manager_user_id FROM tasks t "
        "JOIN hires h ON h.id=t.hire_id "
        "WHERE t.work_state NOT IN ('COMPLETED','CANCELLED') AND h.employment_status!='WITHDRAWN'"
    ).fetchall()
    for task in rows:
        due = date.fromisoformat(task["due_date"])
        days_overdue = (current - due).days
        common = {"hire_id": task["hire_id"], "task_id": task["id"]}
        label = f"{task['title']} for {task['hire_name']}"
        if days_overdue == -2:
            created += notify(
                connection,
                task["owner_user_id"],
                "DEADLINE_SOON",
                "Task due in 2 days",
                label,
                f"soon:{task['id']}:{due}",
                **common,
            )
        if days_overdue <= 0:
            continue
        created += notify(
            connection,
            task["owner_user_id"],
            "OVERDUE",
            "Task overdue",
            f"{label} was due on {due}.",
            f"overdue:{task['id']}:{current}",
            **common,
        )
        if days_overdue >= 1 and task["manager_user_id"] != task["owner_user_id"]:
            created += notify(
                connection,
                task["manager_user_id"],
                "ESCALATION",
                "Overdue task escalated to you",
                f"{label} is {days_overdue} day(s) overdue.",
                f"esc-mgr:{task['id']}:{current}",
                **common,
            )
        if days_overdue >= 2 or task["critical"]:
            hr_users = connection.execute(
                "SELECT u.id FROM users u JOIN user_scopes s ON s.user_id=u.id "
                "WHERE u.role='HR' AND u.active=1 AND s.hire_id=?",
                (task["hire_id"],),
            ).fetchall()
            for user in hr_users:
                created += notify(
                    connection,
                    user["id"],
                    "ESCALATION",
                    "Overdue task escalated to HR",
                    f"{label} is {days_overdue} day(s) overdue.",
                    f"esc-hr:{task['id']}:{current}",
                    **common,
                )
    return created


def week_window(start: date) -> tuple[date, date]:
    return start, start + timedelta(days=7)
