"""Security acceptance: every route is authenticated, and scope cannot be probed."""

import sqlite3

import pytest
from app.main import app
from app.shared.db import connect, initialize

PUBLIC = {"/api/health", "/api/bootstrap", "/api/sessions"}


def api_routes():
    for path, methods in app.openapi()["paths"].items():
        if path not in PUBLIC:
            for method in methods:
                yield method.upper(), path


def test_every_business_route_requires_a_session(world):
    routes = list(api_routes())
    assert len(routes) > 40
    for method, path in routes:
        filled = path.replace("{", "").replace("}", "")
        response = world.client.request(method, filled, json={})
        assert response.status_code == 401, f"{method} {path} returned {response.status_code}"


def test_no_browser_supplied_role_is_trusted(world):
    headers = {**world.headers("U_PRIYA"), "X-Role": "HR", "X-User-Id": "U_HR"}
    response = world.client.get("/api/analytics/overview", headers=headers)
    assert response.status_code == 403


@pytest.mark.parametrize(
    "user,path",
    [
        ("U_PRIYA", "/analytics/overview"),
        ("U_MANAGER", "/audit-events"),
        ("U_IT", "/ai-runs"),
        ("U_PAYROLL", "/metrics"),
        ("U_TRAINING", "/documents/queue"),
        ("U_PRIYA", "/assistant/escalations"),
        ("U_PRIYA", "/reference"),
    ],
)
def test_role_restricted_reads(world, user, path):
    assert world.get(user, path).status_code == 403


def test_cross_hire_access_is_an_indistinguishable_404(world):
    hire = world.create_hire()
    denied = world.get("U_MANAGER2", f"/hires/{hire['id']}")
    missing = world.get("U_MANAGER2", "/hires/HIRE_missing")
    assert denied.status_code == missing.status_code == 404
    assert denied.json() == missing.json()
    assert world.get("U_MANAGER2", f"/hires/{hire['id']}/plan").status_code == 404
    assert world.get("U_MANAGER2", f"/hires/{hire['id']}/history").status_code == 404


def test_hr_is_not_globally_exempt(world):
    hire = world.create_hire()
    with connect() as connection:
        connection.execute(
            "DELETE FROM user_scopes WHERE user_id='U_HR' AND hire_id=?", (hire["id"],)
        )
    assert world.get("U_HR", f"/hires/{hire['id']}").status_code == 404


def test_employee_cannot_create_hires_or_touch_other_people(world):
    other = world.create_hire()
    world.create_hire(
        display_name="Ravi Kumar", employee_user_id="U_RAVI", work_email="r@northstar.example"
    )
    assert world.get("U_RAVI", f"/hires/{other['id']}").status_code == 404
    assert world.post("U_RAVI", "/hires", {}).status_code in (403, 422)
    upload = world.upload("U_RAVI", other["id"], "education", "x.txt", b"text\n")
    assert upload.status_code == 404


def test_errors_never_leak_paths_or_tracebacks(world, monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("/private/secret/path")

    monkeypatch.setattr("app.planning.service.my_work", explode)
    response = world.get("U_HR", "/my-work")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "/private/secret/path" not in response.text


def test_v1_database_upgrades_only_when_empty(tmp_path):
    path = tmp_path / "old.db"
    connection = sqlite3.connect(path)
    connection.executescript(
        """CREATE TABLE app_info (id INTEGER PRIMARY KEY, project_name TEXT, schema_version INT);
        INSERT INTO app_info VALUES (1, 'DayOne Proof', 1);
        CREATE TABLE users (id TEXT PRIMARY KEY);
        CREATE TABLE hires (id TEXT PRIMARY KEY);
        CREATE TABLE policies (id TEXT PRIMARY KEY);
        CREATE TABLE tasks (id TEXT PRIMARY KEY);
        CREATE TABLE source_records (id TEXT PRIMARY KEY);
        CREATE TABLE cases (id TEXT PRIMARY KEY);"""
    )
    connection.commit()
    initialize(path)
    connection = sqlite3.connect(path)
    assert connection.execute("SELECT schema_version FROM app_info").fetchone()[0] == 2
    connection.close()

    busy = tmp_path / "busy.db"
    connection = sqlite3.connect(busy)
    connection.executescript(
        """CREATE TABLE app_info (id INTEGER PRIMARY KEY, project_name TEXT, schema_version INT);
        INSERT INTO app_info VALUES (1, 'DayOne Proof', 1);
        CREATE TABLE users (id TEXT PRIMARY KEY);
        INSERT INTO users VALUES ('someone');
        CREATE TABLE hires (id TEXT PRIMARY KEY);
        CREATE TABLE policies (id TEXT PRIMARY KEY);
        CREATE TABLE tasks (id TEXT PRIMARY KEY);
        CREATE TABLE source_records (id TEXT PRIMARY KEY);
        CREATE TABLE cases (id TEXT PRIMARY KEY);"""
    )
    connection.commit()
    connection.close()
    with pytest.raises(sqlite3.DatabaseError):
        initialize(busy)


def test_seed_refuses_a_database_with_data(world):
    from fixtures.seed import seed

    from .helpers import PASSWORD

    with pytest.raises(SystemExit):
        seed(PASSWORD)
