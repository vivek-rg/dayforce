"""Concurrency and race condition tests: double approval, asset collision, task racing."""

import concurrent.futures

from .helpers import World


class TestConcurrencyAndRaceConditions:
    def test_double_approval_race_prevented(self, world: World):
        """Two concurrent approval calls on the same proposal must not both succeed."""
        hire = world.create_hire(location_id="BLR-DEMO")
        prop_res = world.post(
            "U_IT",
            f"/hires/{hire['id']}/equipment-requests",
            {"equipment_record_id": "EQ_BLR_22"},
        )
        assert prop_res.status_code == 201
        prop_id = prop_res.json()["id"]

        def approve_call(decision: str):
            return world.post(
                "U_IT",
                f"/proposals/{prop_id}/decisions",
                {"decision": decision, "note": f"Concurrent {decision}"},
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(approve_call, "APPROVE")
            f2 = executor.submit(approve_call, "REJECT")
            r1 = f1.result()
            r2 = f2.result()

        # Exactly one must succeed (200), and the second must be rejected (400 or 409)
        statuses = [r1.status_code, r2.status_code]
        assert 200 in statuses
        assert (400 in statuses) or (409 in statuses)

    def test_same_asset_double_reservation_race_prevented(self, world: World):
        """Two proposals for the same piece of inventory cannot both execute successfully."""
        hire1 = world.create_hire(
            display_name="Hire One", location_id="BLR-DEMO", employee_user_id="U_PRIYA"
        )
        hire2 = world.create_hire(
            display_name="Hire Two", location_id="BLR-DEMO", employee_user_id="U_LEELA"
        )

        # Propose the SAME laptop (EQ_BLR_23) for both hires
        p1_res = world.post(
            "U_IT",
            f"/hires/{hire1['id']}/equipment-requests",
            {"equipment_record_id": "EQ_BLR_23"},
        )
        assert p1_res.status_code == 201
        prop1 = p1_res.json()

        p2_res = world.post(
            "U_IT",
            f"/hires/{hire2['id']}/equipment-requests",
            {"equipment_record_id": "EQ_BLR_23"},
        )
        assert p2_res.status_code == 201
        prop2 = p2_res.json()

        # Approve proposal 1
        res1 = world.post(
            "U_IT",
            f"/proposals/{prop1['id']}/decisions",
            {"decision": "APPROVE", "note": "Approved first"},
        )
        assert res1.status_code == 200

        # Now attempt to approve/execute proposal 2 for the same asset
        res2 = world.post(
            "U_IT",
            f"/proposals/{prop2['id']}/decisions",
            {"decision": "APPROVE", "note": "Approved second"},
        )
        assert res2.status_code == 200

        # Process work queue
        world.work()

        # Verify exactly one proposal succeeded and the other failed due to asset collision
        states = {
            world.get("U_IT", f"/proposals/{p['id']}").json()["action_state"]
            for p in (prop1, prop2)
        }
        assert states == {"SUCCEEDED", "FAILED"}

    def test_task_optimistic_concurrency_conflict(self, world: World):
        """Completing a task with an outdated version must return 409 CONFLICT."""
        hire = world.create_hire(location_id="BLR-DEMO")
        task = world.task(hire["id"], "Submit government ID")

        # Complete task once -> succeeds
        res1 = world.post(
            "U_PRIYA",
            f"/tasks/{task['id']}/complete",
            {"expected_version": task["version"]},
        )
        assert res1.status_code == 200

        # Attempt to complete again with the OLD version -> returns 409 CONFLICT
        res2 = world.post(
            "U_PRIYA",
            f"/tasks/{task['id']}/complete",
            {"expected_version": task["version"]},
        )
        assert res2.status_code == 409
        assert res2.json()["error"]["code"] == "STALE_VERSION"
