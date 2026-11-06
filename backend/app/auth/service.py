"""Sessions, password hashing and object-level authorization."""

import base64
import hashlib
import hmac
import re
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta

from fastapi import Request

from app.notifications.service import notify_role
from app.shared.contracts import PasswordReset, Role, Session, TemporaryPassword, User
from app.shared.db import connect
from app.shared.errors import fail, not_found
from app.shared.util import new_id, now_iso

SESSION_HOURS = 8
MAX_FAILURES = 5
LOCK_MINUTES = 5
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
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
        account = connection.execute(
            "SELECT id FROM users WHERE id=? OR email=? COLLATE NOCASE", (user_id, user_id)
        ).fetchone()
        user_id = account["id"] if account else user_id
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
        session = _new_session(connection, user_id)
        connection.execute("DELETE FROM sessions WHERE expires_at < ?", (now_iso(),))
    return session


def _new_session(connection: sqlite3.Connection, user_id: str) -> Session:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(hours=SESSION_HOURS)
    connection.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?,?,?)",
        (_token_hash(token), user_id, expires.strftime("%Y-%m-%dT%H:%M:%SZ")),
    )
    return Session(access_token=token, expires_at=expires, user=load_user(connection, user_id))


def create_account(display_name: str, email: str, password: str) -> Session:
    """Self sign-up. Always a new employee with no access until HR links them to a plan."""
    address = email.strip()
    if not EMAIL_PATTERN.fullmatch(address):
        fail(422, "VALIDATION_ERROR", "Enter a valid email address.")
    user_id = new_id("USR")
    with connect() as connection:
        if connection.execute(
            "SELECT 1 FROM users WHERE email=? COLLATE NOCASE", (address,)
        ).fetchone():
            fail(409, "EMAIL_IN_USE", "An account with this email already exists. Sign in instead.")
        connection.execute(
            "INSERT INTO users (id, display_name, email, role, password_hash) "
            "VALUES (?,?,?,'EMPLOYEE',?)",
            (user_id, display_name.strip(), address, hash_password(password)),
        )
        return _new_session(connection, user_id)


def request_password_reset(email: str) -> None:
    """Tells HR. The reply never reveals whether the account exists."""
    with connect() as connection:
        row = connection.execute(
            "SELECT id, display_name FROM users WHERE email=? COLLATE NOCASE AND active=1",
            (email.strip(),),
        ).fetchone()
        if row is None:
            return
        reset_id = new_id("RST")
        cursor = connection.execute(
            "INSERT OR IGNORE INTO password_resets (id, user_id, state, created_at) "
            "VALUES (?,?,'OPEN',?)",
            (reset_id, row["id"], now_iso()),
        )
        if cursor.rowcount == 1:
            notify_role(
                connection,
                "HR",
                None,
                kind="PASSWORD_RESET",
                title="Password reset requested",
                body=f"{row['display_name']} asked for a password reset. See Settings.",
                dedupe_key=f"reset:{reset_id}",
            )


def open_password_resets(connection: sqlite3.Connection) -> list[PasswordReset]:
    rows = connection.execute(
        "SELECT r.id, r.created_at, u.display_name, u.email, u.role FROM password_resets r "
        "JOIN users u ON u.id=r.user_id WHERE r.state='OPEN' ORDER BY r.created_at, r.rowid"
    ).fetchall()
    return [
        PasswordReset(
            id=row["id"],
            display_name=row["display_name"],
            email=row["email"],
            role=row["role"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def issue_temporary_password(reset_id: str, actor: User) -> TemporaryPassword:
    """Shown once to HR. Existing sessions end, and any lockout on the account clears."""
    temporary = "temp-" + secrets.token_urlsafe(12)
    with connect() as connection:
        row = connection.execute(
            "SELECT r.user_id, u.display_name FROM password_resets r "
            "JOIN users u ON u.id=r.user_id WHERE r.id=? AND r.state='OPEN'",
            (reset_id,),
        ).fetchone()
        if row is None:
            not_found()
        connection.execute(
            "UPDATE users SET password_hash=? WHERE id=?",
            (hash_password(temporary), row["user_id"]),
        )
        connection.execute("DELETE FROM sessions WHERE user_id=?", (row["user_id"],))
        connection.execute("DELETE FROM login_attempts WHERE user_id=?", (row["user_id"],))
        connection.execute(
            "UPDATE password_resets SET state='DONE', resolved_by=?, resolved_at=? WHERE id=?",
            (actor.id, now_iso(), reset_id),
        )
    return TemporaryPassword(display_name=row["display_name"], temporary_password=temporary)


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
