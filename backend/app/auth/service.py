"""Sessions, password hashing and object-level authorization."""

import base64
import hashlib
import hmac
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta

from fastapi import Request

from app.shared.contracts import Role, Session, User
from app.shared.db import connect
from app.shared.errors import fail, not_found
from app.shared.util import now_iso

SESSION_HOURS = 8
MAX_FAILURES = 5
LOCK_MINUTES = 5
_SCRYPT = {"n": 2**14, "r": 8, "p": 1, "dklen": 32}


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)
    return "scrypt$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(derived).decode()


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, expected = stored.split("$")
        derived = hashlib.scrypt(password.encode(), salt=base64.b64decode(salt), **_SCRYPT)
        return hmac.compare_digest(derived, base64.b64decode(expected))
    except ValueError:
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def load_user(connection: sqlite3.Connection, user_id: str) -> User | None:
    row = connection.execute(
        "SELECT id, display_name, role FROM users WHERE id=? AND active=1", (user_id,)
    ).fetchone()
    if row is None:
        return None
    scopes = connection.execute(
        "SELECT hire_id FROM user_scopes WHERE user_id=? ORDER BY hire_id", (user_id,)
    ).fetchall()
    return User(
        id=row["id"],
        display_name=row["display_name"],
        role=Role(row["role"]),
        hire_ids=[item["hire_id"] for item in scopes],
    )


def login(user_id: str, password: str) -> Session:
    invalid = "Those credentials were not recognised."
    now = datetime.now(UTC)
    with connect() as connection:
        attempt = connection.execute(
            "SELECT failures, locked_until FROM login_attempts WHERE user_id=?", (user_id,)
        ).fetchone()
        if attempt and attempt["locked_until"] and attempt["locked_until"] > now_iso():
            fail(429, "TOO_MANY_ATTEMPTS", "Too many failed attempts. Try again in a few minutes.")
        row = connection.execute(
            "SELECT password_hash FROM users WHERE id=? AND active=1", (user_id,)
        ).fetchone()
        if row is None or not verify_password(password, row["password_hash"]):
            failures = (attempt["failures"] if attempt else 0) + 1
            locked = None
            if failures >= MAX_FAILURES:
                locked = (now + timedelta(minutes=LOCK_MINUTES)).strftime("%Y-%m-%dT%H:%M:%SZ")
                failures = 0
            if row is not None:
                connection.execute(
                    "INSERT INTO login_attempts (user_id, failures, locked_until) VALUES (?,?,?) "
                    "ON CONFLICT(user_id) DO UPDATE SET failures=excluded.failures, "
                    "locked_until=excluded.locked_until",
                    (user_id, failures, locked),
                )
                connection.commit()
            fail(401, "UNAUTHENTICATED", invalid)
        connection.execute("DELETE FROM login_attempts WHERE user_id=?", (user_id,))
        token = secrets.token_urlsafe(32)
        expires = now + timedelta(hours=SESSION_HOURS)
        connection.execute(
            "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?,?,?)",
            (_token_hash(token), user_id, expires.strftime("%Y-%m-%dT%H:%M:%SZ")),
        )
        connection.execute("DELETE FROM sessions WHERE expires_at < ?", (now_iso(),))
        user = load_user(connection, user_id)
    return Session(access_token=token, expires_at=expires, user=user)


def _bearer(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    return token.strip() if scheme.lower() == "bearer" and token.strip() else None


def require_user(request: Request) -> User:
    """FastAPI dependency. Identity and scopes are re-read on every request."""
    token = _bearer(request)
    if token is None:
        fail(401, "UNAUTHENTICATED", "Sign in to continue.")
    with connect() as connection:
        row = connection.execute(
            "SELECT user_id FROM sessions WHERE token_hash=? AND expires_at > ?",
            (_token_hash(token), now_iso()),
        ).fetchone()
        user = load_user(connection, row["user_id"]) if row else None
    if user is None:
        fail(401, "UNAUTHENTICATED", "Your session has expired. Sign in again.")
    return user


def logout(request: Request) -> None:
    token = _bearer(request)
    with connect() as connection:
        connection.execute("DELETE FROM sessions WHERE token_hash=?", (_token_hash(token or ""),))


def require_hire_scope(user: User, hire_id: str) -> None:
    """Out-of-scope and unknown hires are the same 404, including for HR."""
    if hire_id not in user.hire_ids:
        not_found()
