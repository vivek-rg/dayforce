import sqlite3

import pytest
from app.main import app
from app.shared.contracts import NextStep, PayrollInput
from app.shared.db import connect, initialize
from fastapi.testclient import TestClient
from pydantic import ValidationError


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def test_health_and_db_bootstrap(client):
    assert client.get("/api/health").json() == {
        "status": "ok",
        "database": "ok",
        "schema_version": 2,
    }
    assert client.get("/api/bootstrap").json()["project_name"] == "OnboardIQ"
    with connect() as connection:
        connection.execute("UPDATE app_info SET project_name=? WHERE id=1", ("Database proof",))
    assert client.get("/api/bootstrap").json()["project_name"] == "Database proof"


def test_health_alias_uses_readiness_without_changing_api_contract(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == client.get("/api/health").json()
    assert "/health" not in app.openapi()["paths"]


def test_initialize_is_repeatable_and_preserves_existing_data(client):
    with connect() as connection:
        connection.execute("UPDATE app_info SET project_name=? WHERE id=1", ("Keep me",))
    initialize()
    assert client.get("/api/bootstrap").json()["project_name"] == "Keep me"


def test_business_routes_are_honest_stubs(client):
    # As owners replace stubs, their own feature tests take over the behavior contract.
    for route in app.routes:
        endpoint = getattr(route, "endpoint", None)
        if (
            endpoint
            and "not_implemented" in endpoint.__code__.co_names
            and "GET" in getattr(route, "methods", set())
            and "{" not in route.path
        ):
            response = client.get(route.path)
            assert response.status_code == 501
            assert response.json()["error"]["code"] == "FEATURE_NOT_IMPLEMENTED"


def test_validation_does_not_echo_password(client):
    response = client.post("/api/sessions", json={"user_id": "u", "password": "secret"})
    assert response.status_code == 422
    assert "secret" not in response.text
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_unknown_api_is_not_spa_success(client):
    assert client.get("/api/does-not-exist").status_code == 404


def test_no_payroll_secret_fields_or_model_supplied_identity():
    with pytest.raises(ValidationError):
        PayrollInput(
            category="payroll", profile_created=True, setup_confirmed=False, bank="private"
        )
    with pytest.raises(ValidationError):
        NextStep.model_validate(
            {
                "next_step": {
                    "step": "read",
                    "tool": "get_hire_context",
                    "hire_id": "OTHER",
                    "reason_summary": "Read",
                }
            }
        )
    with pytest.raises(ValidationError):
        NextStep.model_validate(
            {
                "next_step": {
                    "step": "read",
                    "tool": "execute_sql",
                    "reason_summary": "Read",
                }
            }
        )


def test_database_enforces_foreign_keys_and_unique_event_ids(client):
    with connect() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO user_scopes VALUES ('missing', 'missing')")


@pytest.mark.parametrize("path", ["/api/health", "/health"])
def test_health_reports_db_failure_without_private_path(client, monkeypatch, tmp_path, path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "missing" / "private.db"))
    response = client.get(path)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DATABASE_UNAVAILABLE"
    assert "private.db" not in response.text
