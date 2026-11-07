"""API boundary, fuzzing, and payload validation tests."""

from .helpers import World


class TestApiValidationAndBoundaryDefenses:
    def test_malformed_json_returns_400(self, world: World):
        """Invalid JSON syntax must return HTTP 400 or 422 Bad Request."""
        res = world.client.post(
            "/api/sessions",
            content='{"user_id": "U_HR", "password": invalid_json_here}',
            headers={"Content-Type": "application/json"},
        )
        assert res.status_code in (400, 422)
        assert "error" in res.json()

    def test_extra_fields_strictly_forbidden(self, world: World):
        """Pydantic model must reject unknown/extra fields with 422 VALIDATION_ERROR."""
        res = world.post(
            "U_HR",
            "/hires",
            {
                "display_name": "Test Extra",
                "role": "engineer",
                "location_id": "BLR-DEMO",
                "work_mode": "office",
                "start_date": "2026-12-01",
                "manager_user_id": "U_MANAGER",
                "employee_user_id": "U_PRIYA",
                "department_id": "DEP_ENG",
                "designation": "Developer",
                "work_email": "test@northstar.example",
                "worker_type": "employee",
                "unauthorized_admin_override": True,  # Extra forbidden field
            },
        )
        assert res.status_code == 422
        error = res.json()["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert any("extra" in d["message"].lower() for d in error["details"])

    def test_oversized_string_payload_rejected(self, world: World):
        """Field length constraints must reject excessively large input strings."""
        huge_name = "A" * 5000  # Exceeds max_length of display_name (200)
        res = world.post(
            "U_HR",
            "/hires",
            {
                "display_name": huge_name,
                "role": "engineer",
                "location_id": "BLR-DEMO",
                "work_mode": "office",
                "start_date": "2026-12-01",
                "manager_user_id": "U_MANAGER",
                "employee_user_id": "U_PRIYA",
                "department_id": "DEP_ENG",
                "designation": "Developer",
                "work_email": "huge@northstar.example",
                "worker_type": "employee",
            },
        )
        assert res.status_code == 422
        assert res.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_empty_request_body_rejected(self, world: World):
        """Posting empty dict or empty body to an endpoint requiring body must return 422."""
        res = world.post("U_HR", "/hires", {})
        assert res.status_code == 422

    def test_unauthenticated_requests_consistently_blocked(self, world: World):
        """Endpoints requiring auth must uniformly reject missing headers with 401."""
        endpoints = [
            ("GET", "/api/me"),
            ("GET", "/api/hires"),
            ("GET", "/api/analytics/overview"),
            ("GET", "/api/review-inbox"),
            ("GET", "/api/documents/queue"),
            ("GET", "/api/notifications"),
        ]
        for method, path in endpoints:
            if method == "GET":
                res = world.client.get(path)
            else:
                res = world.client.post(path, json={})
            assert res.status_code == 401, (
                f"{method} {path} did not return 401, got {res.status_code}"
            )
            assert res.json()["error"]["code"] == "UNAUTHENTICATED"
