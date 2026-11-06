"""Small shared helpers: IDs, UTC timestamps and the sanitized audit write."""

import json
import sqlite3
import uuid
from datetime import UTC, date, datetime


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def today() -> date:
    return datetime.now(UTC).date()


def audit(
    connection: sqlite3.Connection,
    hire_id: str,
    event_type: str,
    summary: str,
    actor: str | None = None,
    case_id: str | None = None,
    action_id: str | None = None,
    event_id: str | None = None,
) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO audit_events "
        "(id, event_id, hire_id, case_id, actor_user_id, action_id, event_type, summary, "
        "created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            new_id("AUD"),
            event_id or new_id("EVT"),
            hire_id,
            case_id,
            actor,
            action_id,
            event_type,
            summary[:500],
            now_iso(),
        ),
    )


def loads(value: str | None):
    return json.loads(value) if value else None
