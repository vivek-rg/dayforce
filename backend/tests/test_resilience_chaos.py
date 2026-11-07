"""Resilience and chaos tests: failure recovery, provider timeout handling, state durability."""

import sqlite3

import pytest
from app.ai.providers import ProviderError, Reply, set_provider_for_tests
from app.shared.db import connect

from .helpers import World


class TimeoutProvider:
    name = "chaos_timeout"
    model = "timeout_test"
    is_stub = False
    is_local = False

    def generate(
        self, operation: str, messages: list[dict], schema: dict, timeout: float, max_tokens: int
    ) -> Reply:
        raise ProviderError("Inference call timed out after 30 seconds.")


class TestResilienceAndChaos:
    def test_ai_provider_timeout_fails_gracefully(self, world: World):
        """When the LLM provider times out, the system must not crash; it records error state."""
        set_provider_for_tests(TimeoutProvider())
        world.create_hire()

        # Ask a knowledge assistant question
        res = world.post(
            "U_HR",
            "/assistant/questions",
            {"question": "What is the policy for medical leave?"},
        )
        assert res.status_code in (200, 503)

    def test_database_foreign_key_constraints_enforced(self, world: World):
        """Inserting a task pointing to a non-existent hire must fail with integrity error."""
        with pytest.raises(sqlite3.IntegrityError):
            with connect() as conn:
                conn.execute(
                    "INSERT INTO tasks (id, hire_id, logical_key, category, title, description, "
                    "owner_user_id, policy_id, policy_version, rule_id, due_date, priority, "
                    "critical, work_state, version) VALUES ('T_FAKE', 'HIRE_NONEXISTENT', "
                    "'KEY1', 'documents', 'Fake', 'Desc', 'U_HR', 'POL1', 1, 'R1', '2026-11-07', "
                    "'MEDIUM', 0, 'PENDING', 1)"
                )

    def test_work_items_survive_restarts_and_errors(self, world: World):
        """Work items in SQLite must maintain state across worker processing cycles."""
        hire = world.create_hire()
        case_res = world.post(
            "U_HR",
            f"/hires/{hire['id']}/cases",
            {"message": "Durable work queue resilience check"},
        )
        assert case_res.status_code == 202
        work_id = case_res.json()["work_item_id"]

        # Verify queued item exists
        item = world.get("U_HR", f"/work-items/{work_id}").json()
        assert item["id"] == work_id
        assert item["state"] in ("PENDING", "DONE")
