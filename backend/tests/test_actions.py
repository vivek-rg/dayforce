import json
from datetime import UTC, datetime, timedelta

from app.actions.service import execute_approved_action
from app.shared.db import connect


def reserve(world, hire, device="EQ_HYD_07", user="U_IT"):
    return world.post(
        user, f"/hires/{hire['id']}/equipment-requests", {"equipment_record_id": device}
    )


def test_reservation_needs_it_approval_and_reads_back_collection_pending(world):
    hire = world.create_hire()
    response = reserve(world, hire, user="U_MANAGER")
    assert response.status_code == 201, response.text
    proposal = response.json()
    assert proposal["reviewer_role"] == "IT"
    assert world.source("U_IT", "equipment", "EQ_HYD_07")["payload"]["state"] == "AVAILABLE"
    assert world.task(hire["id"], "Record equipment handover")["evidence_result"] == "UNKNOWN"
    decision = world.post(
        "U_IT", f"/proposals/{proposal['id']}/decisions", {"decision": "APPROVE"}
    ).json()
    assert world.get("U_IT", f"/proposals/{proposal['id']}").json()["action_state"] == "PENDING"
    world.work()
    finished = world.get("U_IT", f"/proposals/{proposal['id']}").json()
    assert finished["action_state"] == "SUCCEEDED"
    assert finished["outcome"] == "LAPTOP_07 reserved; collection pending."
    assert "delivered" not in finished["outcome"].lower()
    assert decision["action_id"]
    checks = {c["check_type"]: c for c in world.plan("U_HR", hire["id"])["checks"]}
    assert checks["device_handover_recorded"]["result"] == "UNKNOWN"
    assert checks["device_handover_recorded"]["reason_code"] == "RESERVED_COLLECTION_PENDING"


def test_wrong_reviewer_and_cross_hire_are_denied(world):
    hire = world.create_hire()
    proposal = reserve(world, hire).json()
    url = f"/proposals/{proposal['id']}/decisions"
    assert world.post("U_HR", url, {"decision": "APPROVE"}).status_code == 403
    assert world.post("U_PRIYA", url, {"decision": "APPROVE"}).status_code == 403
    assert world.post("U_MANAGER2", url, {"decision": "APPROVE"}).status_code == 404


def test_rejection_runs_nothing(world):
    hire = world.create_hire()
    proposal = reserve(world, hire).json()
    world.post("U_IT", f"/proposals/{proposal['id']}/decisions", {"decision": "REJECT"})
    world.work()
    assert world.source("U_IT", "equipment", "EQ_HYD_07")["payload"]["state"] == "AVAILABLE"
    assert world.get("U_IT", f"/proposals/{proposal['id']}").json()["action_state"] is None


def test_duplicate_decision_is_idempotent_and_conflict_is_refused(world):
    hire = world.create_hire()
    proposal = reserve(world, hire).json()
    url = f"/proposals/{proposal['id']}/decisions"
    first = world.post("U_IT", url, {"decision": "APPROVE"}).json()
    second = world.post("U_IT", url, {"decision": "APPROVE"}).json()
    assert first == second
    assert world.post("U_IT", url, {"decision": "REJECT"}).status_code == 409
    world.work()
    with connect() as connection:
        version = connection.execute(
            "SELECT version FROM source_records WHERE id='EQ_HYD_07'"
        ).fetchone()[0]
        count = connection.execute("SELECT COUNT(*) FROM actions").fetchone()[0]
    assert version == 2 and count == 1


def test_repeating_the_executor_cannot_repeat_the_effect(world):
    hire = world.create_hire()
    proposal = reserve(world, hire).json()
    action = world.post(
        "U_IT", f"/proposals/{proposal['id']}/decisions", {"decision": "APPROVE"}
    ).json()["action_id"]
    assert execute_approved_action(action).state == "SUCCEEDED"
    assert execute_approved_action(action).state == "SUCCEEDED"
    with connect() as connection:
        version = connection.execute(
            "SELECT version FROM source_records WHERE id='EQ_HYD_07'"
        ).fetchone()[0]
    assert version == 2


def test_stale_inputs_block_approval(world):
    hire = world.create_hire()
    proposal = reserve(world, hire).json()
    with connect() as connection:
        connection.execute(
            "UPDATE hires SET profile_version=profile_version+1 WHERE id=?", (hire["id"],)
        )
    response = world.post("U_IT", f"/proposals/{proposal['id']}/decisions", {"decision": "APPROVE"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STALE_VERSION"


def test_expired_proposal_cannot_be_approved(world):
    hire = world.create_hire()
    proposal = reserve(world, hire).json()
    past = (datetime.now(UTC) - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with connect() as connection:
        connection.execute("UPDATE proposals SET expires_at=?", (past,))
    response = world.post("U_IT", f"/proposals/{proposal['id']}/decisions", {"decision": "APPROVE"})
    assert response.status_code == 409


def test_inventory_race_affects_zero_rows_and_fails_honestly(world):
    first = world.create_hire()
    second = world.create_hire(
        display_name="Ravi Kumar", employee_user_id="U_RAVI", work_email="r@northstar.example"
    )
    one = reserve(world, first).json()
    two = reserve(world, second).json()
    for proposal in (one, two):
        assert (
            world.post(
                "U_IT", f"/proposals/{proposal['id']}/decisions", {"decision": "APPROVE"}
            ).status_code
            == 200
        )
    world.work()
    states = {world.get("U_IT", f"/proposals/{p['id']}").json()["action_state"] for p in (one, two)}
    assert states == {"SUCCEEDED", "FAILED"}
    payload = world.source("U_IT", "equipment", "EQ_HYD_07")["payload"]
    assert payload["assignee_hire_id"] == first["id"]


def test_device_at_the_wrong_location_cannot_be_proposed(world):
    hire = world.create_hire(location_id="HYD-DEMO")
    assert reserve(world, hire, "EQ_BLR_22").status_code == 409


def test_reservation_cannot_bypass_approval_through_source_write(world):
    hire = world.create_hire()
    body = {
        "expected_version": 0,
        "payload": {
            "category": "equipment",
            "asset_tag": "HACK_1",
            "location_id": "HYD-DEMO",
            "state": "RESERVED",
            "assignee_hire_id": hire["id"],
        },
    }
    response = world.put("U_IT", f"/hires/{hire['id']}/sources/hack", body)
    assert response.status_code == 409


def test_location_change_preserves_history_and_rewrites_only_the_future(world):
    hire = world.create_hire(location_id="HYD-DEMO")
    assert world.complete("U_PRIYA", hire["id"], "Submit government ID").status_code == 200
    completed = world.task(hire["id"], "Submit government ID")
    old_badge = world.task(hire["id"], "Issue Hyderabad office badge")
    proposal = world.post(
        "U_HR",
        f"/hires/{hire['id']}/change-previews",
        {"location_id": "BLR-DEMO", "expected_profile_version": 1},
    ).json()
    assert proposal["plan_diff"]["create"] == ["Issue Bengaluru office badge"]
    assert proposal["plan_diff"]["cancel"] == [old_badge["id"]]
    assert completed["id"] in proposal["plan_diff"]["preserve"]
    assert world.get("U_HR", f"/hires/{hire['id']}").json()["location_id"] == "HYD-DEMO"
    world.post("U_HR", f"/proposals/{proposal['id']}/decisions", {"decision": "APPROVE"})
    world.work()
    fresh = world.get("U_HR", f"/hires/{hire['id']}").json()
    assert fresh["location_id"] == "BLR-DEMO" and fresh["profile_version"] == 2
    assert world.task(hire["id"], "Submit government ID")["work_state"] == "COMPLETED"
    assert world.task(hire["id"], "Issue Hyderabad office badge")["work_state"] == "CANCELLED"
    assert world.task(hire["id"], "Issue Bengaluru office badge")["work_state"] == "PENDING"


def test_source_authority_by_category(world):
    hire = world.create_hire()
    hire_id = hire["id"]
    payroll_id = f"payroll_{hire_id}_main"
    payload = {
        "category": "payroll",
        "profile_created": False,
        "setup_confirmed": True,
    }
    url = f"/hires/{hire_id}/sources/{payroll_id}"
    assert world.put("U_HR", url, {"expected_version": 1, "payload": payload}).status_code == 403
    assert (
        world.put("U_PAYROLL", url, {"expected_version": 1, "payload": payload}).status_code == 422
    )
    payload["profile_created"] = True
    assert (
        world.put("U_PAYROLL", url, {"expected_version": 9, "payload": payload}).status_code == 409
    )
    assert (
        world.put("U_PAYROLL", url, {"expected_version": 1, "payload": payload}).status_code == 200
    )
    benefits = {
        "expected_version": 1,
        "payload": {"category": "benefits", "state": "ENROLLED"},
    }
    benefits_url = f"/hires/{hire_id}/sources/benefits_{hire_id}_main"
    assert world.put("U_PRIYA", benefits_url, benefits).status_code == 403
    benefits["payload"]["state"] = "DECLINED"
    assert world.put("U_PRIYA", benefits_url, benefits).status_code == 200


def test_payroll_cannot_hold_bank_numbers(world):
    hire = world.create_hire()
    url = f"/hires/{hire['id']}/sources/payroll_{hire['id']}_main"
    body = {
        "expected_version": 1,
        "payload": {
            "category": "payroll",
            "profile_created": True,
            "setup_confirmed": False,
            "account_number": "000000",
        },
    }
    response = world.put("U_PAYROLL", url, body)
    assert response.status_code == 422
    assert "000000" not in response.text
    with connect() as connection:
        rows = connection.execute("SELECT payload_json FROM source_records").fetchall()
    assert "account_number" not in json.dumps([row[0] for row in rows])


def test_policy_change_after_proposal_blocks_approval(world):
    hire = world.create_hire()
    proposal = reserve(world, hire).json()

    with connect() as connection:
        task = connection.execute(
            "SELECT policy_id, policy_version FROM tasks WHERE hire_id=? LIMIT 1",
            (hire["id"],),
        ).fetchone()

        policy_id = task["policy_id"]
        old_version = task["policy_version"]
        new_version = old_version + 1

        connection.execute(
            """
            INSERT INTO policies (
                id, version, approved_by, effective_from, effective_to,
                scope_json, sections_json, rules_json
            )
            SELECT
                id, ?, approved_by, effective_from, effective_to,
                scope_json, sections_json, rules_json
            FROM policies
            WHERE id=? AND version=?
            """,
            (new_version, policy_id, old_version),
        )

        connection.execute(
            """
            UPDATE tasks
            SET policy_version=?
            WHERE hire_id=? AND policy_id=?
            """,
            (new_version, hire["id"], policy_id),
        )

    response = world.post(
        "U_IT",
        f"/proposals/{proposal['id']}/decisions",
        {"decision": "APPROVE"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STALE_VERSION"
