"""Defensive security test suite: OWASP Top 10, IDOR, Injection, RBAC, Rate Limiting."""

import json

import pytest

from .helpers import PASSWORD, World


class TestAuthenticationAndAuthorizationSecurity:
    def test_password_hashes_never_leaked(self, world: World):
        """Verify that password hashes are never exposed via sessions, me, or user lists."""
        res = world.client.post("/api/sessions", json={"user_id": "U_HR", "password": PASSWORD})
        assert res.status_code == 200
        data = res.json()
        assert "password" not in json.dumps(data).lower()
        assert "password_hash" not in json.dumps(data)

        me = world.get("U_HR", "/me")
        assert me.status_code == 200
        assert "password_hash" not in json.dumps(me.json())

    def test_brute_force_lockout_on_login(self, world: World):
        """5 failed login attempts must trigger bounded lockout (HTTP 429)."""
        for _ in range(5):
            res = world.client.post(
                "/api/sessions", json={"user_id": "U_HR", "password": "WrongPassword123!"}
            )
            assert res.status_code == 401

        # 6th attempt must be locked out with 429
        locked = world.client.post(
            "/api/sessions", json={"user_id": "U_HR", "password": "WrongPassword123!"}
        )
        assert locked.status_code == 429
        assert locked.json()["error"]["code"] == "TOO_MANY_ATTEMPTS"

    def test_token_tampering_rejected(self, world: World):
        """Invalid or forged bearer tokens must return 401."""
        tampered_headers = {"Authorization": "Bearer fake_token_abc_123_tampered"}
        res = world.client.get("/api/me", headers=tampered_headers)
        assert res.status_code == 401
        assert res.json()["error"]["code"] == "UNAUTHENTICATED"

    def test_session_revocation_enforced(self, world: World):
        """Once logged out, the token cannot be reused."""
        res = world.client.post("/api/sessions", json={"user_id": "U_HR", "password": PASSWORD})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Verify active
        assert world.client.get("/api/me", headers=headers).status_code == 200

        # Log out
        del_res = world.client.delete("/api/sessions/current", headers=headers)
        assert del_res.status_code == 204

        # Verify revoked
        post_res = world.client.get("/api/me", headers=headers)
        assert post_res.status_code == 401


class TestAccessControlAndIDOR:
    def test_employee_cannot_view_or_enumerate_other_hire(self, world: World):
        """Employees must get 404 (indistinguishable from non-existent) for other hires."""
        arjun = world.create_hire(display_name="Arjun Menon", employee_user_id="U_ARJUN")
        priya = world.create_hire(display_name="Priya Sharma", employee_user_id="U_PRIYA")

        # Priya cannot view Arjun's hire details
        res = world.get("U_PRIYA", f"/hires/{arjun['id']}")
        assert res.status_code == 404

        # Priya can view her own hire details
        own = world.get("U_PRIYA", f"/hires/{priya['id']}")
        assert own.status_code == 200

    def test_employee_cannot_access_administrative_endpoints(self, world: World):
        """Employees must be denied access to HR/IT/admin APIs."""
        # Cannot access password resets
        assert world.get("U_PRIYA", "/password-resets").status_code == 403

        # Cannot access review inbox
        assert world.get("U_PRIYA", "/review-inbox").status_code == 403

        # Cannot access audit log
        assert world.get("U_PRIYA", "/audit-events").status_code == 403

        # Cannot access AI runs
        assert world.get("U_PRIYA", "/ai-runs").status_code == 403

    def test_cross_role_proposal_approval_denied(self, world: World):
        """HR cannot approve IT-scoped proposals, and IT cannot approve HR-scoped proposals."""
        hire = world.create_hire(location_id="BLR-DEMO")

        # IT creates an IT equipment request proposal
        prop_res = world.post(
            "U_IT",
            f"/hires/{hire['id']}/equipment-requests",
            {"equipment_record_id": "EQ_BLR_22"},
        )
        assert prop_res.status_code == 201
        prop_id = prop_res.json()["id"]
        assert prop_res.json()["reviewer_role"] == "IT"

        # HR attempts to approve IT proposal -> 403 (forbidden cross-role approval)
        hr_dec = world.post(
            "U_HR",
            f"/proposals/{prop_id}/decisions",
            {"decision": "APPROVE", "note": "HR illegally approving IT"},
        )
        assert hr_dec.status_code == 403

        # IT approves IT proposal -> 200 Success
        it_dec = world.post(
            "U_IT",
            f"/proposals/{prop_id}/decisions",
            {"decision": "APPROVE", "note": "IT validly approving"},
        )
        assert it_dec.status_code == 200


class TestInjectionDefenses:
    @pytest.mark.parametrize(
        "payload",
        [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT id, password_hash, email, role, display_name FROM users --",
        ],
    )
    def test_sql_injection_in_queries_safely_handled(self, world: World, payload: str):
        """Parameterized queries must treat SQL injections as literal strings without error."""
        # Query in hire search
        res = world.get("U_HR", f"/hires?query={payload}")
        assert res.status_code == 200
        assert isinstance(res.json()["items"], list)

        # Audit events query
        audit_res = world.get("U_HR", f"/audit-events?event_type={payload}")
        assert audit_res.status_code == 200
        assert isinstance(audit_res.json()["items"], list)

    def test_stored_xss_in_hire_metadata_escaped(self, world: World):
        """XSS payloads stored in text fields must be safely preserved as text
        without code execution.
        """
        xss_string = '<script>alert("XSS")</script><img src=x onerror=alert(1)>'
        hire = world.create_hire(designation=xss_string)
        assert hire["designation"] == xss_string

        # Read back
        fetched = world.get("U_HR", f"/hires/{hire['id']}").json()
        assert fetched["designation"] == xss_string

        # Check API content-type is strictly application/json (prevents browser script sniffing)
        res = world.get("U_HR", f"/hires/{hire['id']}")
        assert "application/json" in res.headers["content-type"]
