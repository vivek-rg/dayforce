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


def test_sign_in_works_with_email_in_any_case(world):
    for identifier in ("hema@northstar.example", "HEMA@Northstar.Example", "U_HR"):
        response = world.client.post(
            "/api/sessions", json={"user_id": identifier, "password": PASSWORD}
        )
        assert response.status_code == 200, response.text
        assert response.json()["user"]["id"] == "U_HR"


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


def test_lockout_counts_email_and_id_as_one_account(world):
    for identifier in ["imran@northstar.example", "U_IT"] * 2 + ["imran@northstar.example"]:
        world.client.post(
            "/api/sessions", json={"user_id": identifier, "password": "wrong-password-1"}
        )
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


def signup(world, email="new.person@example.invalid"):
    return world.client.post(
        "/api/accounts",
        json={"display_name": "New Person", "email": email, "password": "a-long-new-password"},
    )


def test_create_account_gives_an_employee_with_no_access(world):
    response = signup(world)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["user"]["role"] == "EMPLOYEE" and body["user"]["hire_ids"] == []
    headers = {"Authorization": "Bearer " + body["access_token"]}
    assert world.client.get("/api/hires", headers=headers).json()["items"] == []
    assert world.client.get("/api/analytics/overview", headers=headers).status_code == 403
    login = world.client.post(
        "/api/sessions",
        json={"user_id": "new.person@example.invalid", "password": "a-long-new-password"},
    )
    assert login.status_code == 200


def test_create_account_cannot_choose_a_role_or_reuse_an_email(world):
    extra = world.client.post(
        "/api/accounts",
        json={
            "display_name": "Sneaky",
            "email": "s@example.invalid",
            "password": "a-long-new-password",
            "role": "HR",
        },
    )
    assert extra.status_code == 422
    assert signup(world, "HEMA@northstar.example").status_code == 409
    assert signup(world, "not-an-email").status_code == 422


def test_hr_can_link_a_new_account_to_a_plan(world):
    user_id = signup(world).json()["user"]["id"]
    available = world.get("U_HR", "/reference").json()["available_employee_user_ids"]
    assert user_id in available
    hire = world.create_hire(employee_user_id=user_id)
    assert hire["employee_user_id"] == user_id


def test_forgot_password_flow(world):
    known = world.client.post("/api/password-resets", json={"email": "priya@northstar.example"})
    unknown = world.client.post("/api/password-resets", json={"email": "nobody@example.invalid"})
    assert known.status_code == unknown.status_code == 202
    assert known.content == unknown.content
    assert world.get("U_PRIYA", "/password-resets").status_code == 403
    world.client.post("/api/password-resets", json={"email": "PRIYA@northstar.example"})
    items = world.get("U_HR", "/password-resets").json()["items"]
    assert [item["email"] for item in items] == ["priya@northstar.example"]
    titles = [n["title"] for n in world.get("U_HR", "/notifications").json()["items"]]
    assert "Password reset requested" in titles

    old_headers = world.headers("U_PRIYA")
    url = f"/password-resets/{items[0]['id']}/temporary-password"
    assert world.post("U_PRIYA", url).status_code == 403
    issued = world.post("U_HR", url).json()
    assert world.client.get("/api/me", headers=old_headers).status_code == 401
    assert (
        world.client.post(
            "/api/sessions", json={"user_id": "U_PRIYA", "password": PASSWORD}
        ).status_code
        == 401
    )
    login = world.client.post(
        "/api/sessions",
        json={"user_id": "priya@northstar.example", "password": issued["temporary_password"]},
    )
    assert login.status_code == 200
    with connect() as connection:
        stored = connection.execute(
            "SELECT password_hash FROM users WHERE id='U_PRIYA'"
        ).fetchone()[0]
    assert issued["temporary_password"] not in stored
    assert world.post("U_HR", url).status_code == 404
    assert world.get("U_HR", "/password-resets").json()["items"] == []
