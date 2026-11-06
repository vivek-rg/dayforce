import sqlite3

from app.auth.permissions import PERMISSIONS, can
from app.shared.contracts import Role
from app.shared.db import connect

from .helpers import PASSWORD


def test_login_me_logout_and_revocation(world):
    headers = world.headers("U_HR")
    assert world.client.get("/api/me", headers=headers).json()["role"] == "HR"
    assert world.client.delete("/api/sessions/current", headers=headers).status_code == 204
    assert world.client.get("/api/me", headers=headers).status_code == 401


def test_missing_and_invalid_tokens_are_401(world):
    assert world.client.get("/api/hires").status_code == 401
    bad = {"Authorization": "Bearer not-a-token"}
    assert world.client.get("/api/hires", headers=bad).status_code == 401


def test_wrong_password_never_reveals_which_part_failed(world):
    wrong = world.client.post(
        "/api/sessions", json={"user_id": "U_HR", "password": "wrong-password-1"}
    )
    missing = world.client.post(
        "/api/sessions", json={"user_id": "U_NOBODY", "password": "wrong-password-1"}
    )
    assert wrong.status_code == missing.status_code == 401
    assert wrong.json() == missing.json()


def test_repeated_failures_lock_the_account_briefly(world):
    for _ in range(5):
        world.client.post("/api/sessions", json={"user_id": "U_IT", "password": "wrong-password-1"})
    locked = world.client.post("/api/sessions", json={"user_id": "U_IT", "password": PASSWORD})
    assert locked.status_code == 429


def test_expired_session_and_deactivated_user_are_denied(world):
    headers = world.headers("U_HR")
    with connect() as connection:
        connection.execute("UPDATE sessions SET expires_at='2000-01-01T00:00:00Z'")
    assert world.client.get("/api/me", headers=headers).status_code == 401
    world._tokens.clear()
    headers = world.headers("U_IT")
    with connect() as connection:
        connection.execute("UPDATE users SET active=0 WHERE id='U_IT'")
    assert world.client.get("/api/me", headers=headers).status_code == 401


def test_raw_tokens_and_passwords_are_not_stored(world):
    headers = world.headers("U_HR")
    token = headers["Authorization"].split()[1]
    with connect() as connection:
        hashes = [row[0] for row in connection.execute("SELECT token_hash FROM sessions")]
        stored = connection.execute("SELECT password_hash FROM users LIMIT 1").fetchone()[0]
    assert token not in hashes
    assert PASSWORD not in stored and stored.startswith("scrypt$")


def test_only_hr_can_verify_and_the_ai_has_no_role():
    assert can(Role.HR, "document.review")
    for role in Role:
        if role != Role.HR:
            assert not can(role, "document.review")
    assert all(isinstance(role, Role) for roles in PERMISSIONS.values() for role in roles)


def test_foreign_keys_are_on(world):
    with connect() as connection:
        try:
            connection.execute("INSERT INTO user_scopes VALUES ('nobody', 'nothing')")
            raised = False
        except sqlite3.IntegrityError:
            raised = True
    assert raised
