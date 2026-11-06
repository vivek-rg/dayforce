from datetime import date, timedelta

import pytest
from app.planning.service import display_status, validate_rules
from app.shared.contracts import DisplayStatus
from app.shared.db import connect
from app.shared.util import today
from fastapi import HTTPException

from .helpers import hire_body


def titles(plan):
    return {task["title"] for task in plan["tasks"]}


def test_engineer_in_bangalore_gets_a_personal_seven_category_plan(world):
    hire = world.create_hire(location_id="BLR-DEMO")
    plan = world.plan("U_HR", hire["id"])
    assert {task["category"] for task in plan["tasks"]} == {
        "documents",
        "equipment",
        "it_access",
        "payroll",
        "benefits",
        "training",
        "manager",
    }
    assert "Issue Bengaluru office badge" in titles(plan)
    assert "Grant VPN and developer tools (simulated)" in titles(plan)
    assert "Issue Hyderabad office badge" not in titles(plan)


def test_remote_sales_and_contractor_plans_really_differ(world):
    sales = world.create_hire(
        display_name="Arjun Menon",
        role="sales_associate",
        work_mode="remote",
        employee_user_id="U_ARJUN",
        department_id="DEP_SALES",
    )
    contractor = world.create_hire(
        display_name="Leela Pillai",
        role="operations_associate",
        worker_type="contractor",
        employee_user_id="U_LEELA",
        department_id="DEP_OPS",
    )
    sales_titles = titles(world.plan("U_HR", sales["id"]))
    contractor_titles = titles(world.plan("U_HR", contractor["id"]))
    assert "Ship a laptop to the remote employee" in sales_titles
    assert "Grant CRM access (simulated)" in sales_titles
    assert "Record equipment handover" not in sales_titles
    assert "Confirm payroll setup" not in contractor_titles
    assert "Complete benefits enrolment" not in contractor_titles


def test_due_dates_follow_the_approved_rule(world):
    start = date.today() + timedelta(days=30)
    hire = world.create_hire(start_date=start.isoformat())
    plan = world.plan("U_HR", hire["id"])
    due = {task["title"]: task["due_date"] for task in plan["tasks"]}
    assert due["Submit government ID"] == (start - timedelta(days=7)).isoformat()
    assert due["Complete benefits enrolment"] == (start + timedelta(days=7)).isoformat()


def test_dependencies_wait_and_release(world):
    hire = world.create_hire()
    assert world.task(hire["id"], "Reserve a laptop")["display_status"] == "BLOCKED"
    assert world.complete("U_PRIYA", hire["id"], "Submit signed employment").status_code == 200
    confirm = world.task(hire["id"], "Confirm work location")
    assert confirm["work_state"] == "PENDING"
    blocked = world.task(hire["id"], "Reserve a laptop")
    response = world.post("U_IT", f"/tasks/{blocked['id']}/complete", {"expected_version": 1})
    assert response.status_code == 409


def test_completion_is_a_claim_not_proof(world):
    hire = world.create_hire()
    response = world.complete("U_PRIYA", hire["id"], "Submit government ID")
    assert response.status_code == 200
    assert response.json()["work_state"] == "COMPLETED"
    assert response.json()["evidence_result"] == "UNKNOWN"
    overview = world.get("U_HR", "/analytics/overview").json()
    assert overview["claims_without_proof"] == 1


def test_only_the_owner_can_act_and_versions_are_enforced(world):
    hire = world.create_hire()
    task = world.task(hire["id"], "Submit government ID")
    url = f"/tasks/{task['id']}/complete"
    assert world.post("U_HR", url, {"expected_version": task["version"]}).status_code == 403
    assert world.post("U_PRIYA", url, {"expected_version": 99}).status_code == 409


def test_hr_reassign_moves_ownership_and_grants_scope(world):
    hire = world.create_hire()
    task = world.task(hire["id"], "Schedule team introductions")
    body = {"expected_version": task["version"], "owner_user_id": "U_MANAGER2"}
    assert world.post("U_IT", f"/tasks/{task['id']}/reassign", body).status_code == 403
    response = world.post("U_HR", f"/tasks/{task['id']}/reassign", body)
    assert response.json()["owner_user_id"] == "U_MANAGER2"
    assert world.get("U_MANAGER2", f"/hires/{hire['id']}").status_code == 200


def test_unsupported_profile_goes_to_manual_review(world):
    with connect() as connection:
        connection.execute("UPDATE policies SET effective_to='2026-01-02'")
    response = world.post("U_HR", "/hires", hire_body())
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "POLICY_REVIEW_REQUIRED"


def test_rule_cycles_and_duplicates_are_rejected():
    with pytest.raises(HTTPException):
        validate_rules([{"id": "A", "depends_on": ["B"]}, {"id": "B", "depends_on": ["A"]}])
    with pytest.raises(HTTPException):
        validate_rules([{"id": "A"}, {"id": "A"}])


@pytest.mark.parametrize(
    "state,evidence,pending,offset,expected",
    [
        ("CANCELLED", None, True, -5, DisplayStatus.CANCELLED),
        ("COMPLETED", "BLOCKED", True, -5, DisplayStatus.COMPLETED),
        ("PENDING", None, True, -5, DisplayStatus.PENDING_APPROVAL),
        ("WAITING_DEPENDENCY", None, False, 5, DisplayStatus.BLOCKED),
        ("PENDING", "BLOCKED", False, 5, DisplayStatus.BLOCKED),
        ("PENDING", None, False, -1, DisplayStatus.OVERDUE),
        ("IN_PROGRESS", None, False, 1, DisplayStatus.IN_PROGRESS),
        ("PENDING", "UNKNOWN", False, 0, DisplayStatus.NOT_STARTED),
    ],
)
def test_display_status_is_a_pure_ordered_mapping(state, evidence, pending, offset, expected):
    now = today()
    assert display_status(state, evidence, pending, now + timedelta(days=offset), now) == expected


def test_overdue_sweep_escalates_without_duplicates(world):
    hire = world.create_hire(start_date=(date.today() + timedelta(days=30)).isoformat())
    past = (date.today() - timedelta(days=2)).isoformat()
    with connect() as connection:
        connection.execute(
            "UPDATE tasks SET due_date=? WHERE hire_id=? AND logical_key='MANAGER_INTRO'",
            (past, hire["id"]),
        )
        connection.execute(
            "UPDATE tasks SET due_date=? WHERE hire_id=? AND logical_key='SUBMIT_ID'",
            (past, hire["id"]),
        )
    assert world.post("U_IT", "/notifications/sweep").status_code == 403
    assert world.post("U_HR", "/notifications/sweep").json()["notifications_created"] > 0
    assert world.post("U_HR", "/notifications/sweep").json()["notifications_created"] == 0
    types = {n["type"] for n in world.get("U_HR", "/notifications").json()["items"]}
    assert "ESCALATION" in types
    manager = [n["title"] for n in world.get("U_MANAGER", "/notifications").json()["items"]]
    assert "Overdue task escalated to you" in manager
    assert world.task(hire["id"], "Submit government ID")["display_status"] == "OVERDUE"


def test_contact_fields_are_filtered_by_role(world):
    hire = world.create_hire(phone="+91 00000 00000", personal_email="p@example.invalid")
    assert world.get("U_HR", f"/hires/{hire['id']}").json()["phone"] == "+91 00000 00000"
    assert world.get("U_PRIYA", f"/hires/{hire['id']}").json()["phone"] == "+91 00000 00000"
    assert world.get("U_MANAGER", f"/hires/{hire['id']}").json()["phone"] is None
    assert world.get("U_IT", f"/hires/{hire['id']}").json()["personal_email"] is None


def test_it_sees_only_its_categories(world):
    hire = world.create_hire()
    categories = {task["category"] for task in world.plan("U_IT", hire["id"])["tasks"]}
    assert categories == {"equipment", "it_access"}
