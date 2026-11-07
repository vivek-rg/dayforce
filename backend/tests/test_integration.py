"""The complete recorded journey through the public API, using the labelled offline rules."""

from datetime import date, timedelta

import pytest
from app.ai.providers import ProviderError, set_provider_for_tests
from app.ai.stub import StubProvider
from app.shared.contracts import utc_now
from app.shared.db import connect

from .helpers import Scripted


def test_full_onboarding_journey(world):
    set_provider_for_tests(StubProvider())

    # 1-2. HR creates Priya. The engine generates a personal plan with no AI.
    hire = world.create_hire(location_id="HYD-DEMO")
    hire_id = hire["id"]
    assert hire["onboarding_status"] == "NOT_STARTED" and hire["tasks_total"] >= 14

    # 3-4. Priya sees her own checklist and submits documents.
    assert [item["id"] for item in world.get("U_PRIYA", "/hires").json()["items"]] == [hire_id]
    assert world.get("U_PRIYA", "/my-work").json()["items"]
    letter = world.upload_fixture(
        "U_PRIYA", hire_id, "signed_employment", "offer_letter_priya.txt"
    ).json()
    identity = world.upload_fixture(
        "U_PRIYA", hire_id, "government_id", "government_id_priya.txt"
    ).json()

    # 5. AI extraction is advisory. Code flags the conflict.
    extraction = world.post("U_HR", f"/documents/{letter['id']}/extractions").json()
    assert extraction["mismatches"][0]["field"] == "work_location"

    # 6. HR reviews. A person verifies.
    queue = world.get("U_HR", "/documents/queue").json()["items"]
    assert {item["id"] for item in queue} == {letter["id"], identity["id"]}
    fresh_letter = next(item for item in queue if item["id"] == letter["id"])
    assert world.review(fresh_letter).json()["state"] == "VERIFIED"
    assert world.review(identity).json()["state"] == "VERIFIED"

    # The investigation asks HR, pauses, then proposes the exact location change.
    case_id = world.post(
        "U_HR", f"/hires/{hire_id}/cases", {"message": "Check location and equipment."}
    ).json()["case_id"]
    world.work()
    case = world.get("U_HR", f"/cases/{case_id}").json()
    assert case["state"] == "WAITING_HUMAN"
    world.post(
        "U_HR",
        f"/questions/{case['questions'][0]['id']}/responses",
        {"answer": "The offer letter is right: Bengaluru."},
    )
    world.work()
    case = world.get("U_HR", f"/cases/{case_id}").json()
    assert case["state"] == "WAITING_APPROVAL"
    location = case["proposals"][0]
    assert "Issue Bengaluru office badge" in location["plan_diff"]["create"]
    world.post("U_HR", f"/proposals/{location['id']}/decisions", {"decision": "APPROVE"})
    world.work()
    assert world.get("U_HR", f"/hires/{hire_id}").json()["location_id"] == "BLR-DEMO"

    # 7. IT gets a separate approval for a Bengaluru device, then sees "collection pending".
    case = world.get("U_HR", f"/cases/{case_id}").json()
    assert case["state"] == "WAITING_APPROVAL"
    inbox = world.get("U_IT", "/review-inbox").json()["items"]
    reservation = next(p for p in inbox if p["decision"] is None)
    assert reservation["payload"] == {
        "action_type": "RESERVE_EQUIPMENT",
        "equipment_record_id": "EQ_BLR_22",
    }
    assert world.get("U_MANAGER", "/review-inbox").status_code == 403
    world.post("U_IT", f"/proposals/{reservation['id']}/decisions", {"decision": "APPROVE"})
    world.work()
    outcome = world.get("U_IT", f"/proposals/{reservation['id']}").json()["outcome"]
    assert outcome == "LAPTOP_22 reserved; collection pending."
    assert world.get("U_HR", f"/cases/{case_id}").json()["state"] == "RESOLVED"

    # A completed handover task with no handover record stays visibly unproven.
    world.complete("U_PRIYA", hire_id, "Submit government ID")
    world.complete("U_PRIYA", hire_id, "Submit signed employment")
    world.complete("U_HR", hire_id, "Confirm work location")
    world.complete("U_IT", hire_id, "Reserve a laptop")
    claimed = world.complete("U_IT", hire_id, "Record equipment handover").json()
    assert claimed["work_state"] == "COMPLETED" and claimed["evidence_result"] == "UNKNOWN"
    assert world.get("U_HR", "/analytics/overview").json()["claims_without_proof"] >= 1
    assert world.get("U_HR", f"/hires/{hire_id}").json()["onboarding_status"] != "COMPLETED"

    # 8. Manager records the buddy and first-week plan.
    manager_url = f"/hires/{hire_id}/sources/manager_{hire_id}_main"
    manager = world.put(
        "U_MANAGER",
        manager_url,
        {
            "expected_version": 0,
            "payload": {
                "category": "manager",
                "buddy_user_id": "U_IT",
                "first_week_plan": "Set up tools, meet the team, ship a small fix.",
            },
        },
    )
    assert manager.status_code == 200, manager.text
    world.complete("U_MANAGER", hire_id, "Assign a buddy")
    world.complete("U_MANAGER", hire_id, "Schedule team introductions")

    # 9-10. Priya asks a policy question and gets a citation.
    answer = world.post(
        "U_PRIYA", "/assistant/questions", {"question": "How do I request a laptop?"}
    ).json()
    assert answer["claims"][0]["citations"][0]["title"] == "Equipment Guide"

    # 11. An overdue task triggers an escalation.
    with connect() as connection:
        connection.execute(
            "UPDATE tasks SET due_date=? WHERE hire_id=? AND logical_key='TRAIN_SECURITY'",
            ((date.today() - timedelta(days=3)).isoformat(), hire_id),
        )
    assert world.post("U_HR", "/notifications/sweep").json()["notifications_created"] >= 1
    assert world.task(hire_id, "security awareness")["display_status"] == "OVERDUE"

    # 12. HR sees analytics and evidence-backed insights.
    overview = world.get("U_HR", "/analytics/overview").json()
    assert overview["tasks_overdue"] == 1 and overview["total_employees"] == 1
    assert world.post("U_HR", "/insights/summaries").status_code == 200
    metrics = world.get("U_HR", "/metrics").json()
    assert {item["operation"] for item in metrics["operations"]} >= {
        "assistant.answer",
        "document.extract",
        "agent.next_step",
        "insights.summarize",
    }
    assert world.get("U_PRIYA", "/metrics").status_code == 403

    # 13. Every owner finishes, proof is recorded, and only then is onboarding complete.
    def write(user, category, source_id, payload):
        record = world.source(user, category, source_id)
        response = world.put(
            user,
            f"/hires/{hire_id}/sources/{source_id}",
            {"expected_version": record["version"], "payload": payload},
        )
        assert response.status_code == 200, response.text

    device = world.source("U_IT", "equipment", "EQ_BLR_22")["payload"]
    device.update(state="HANDED_OVER", handover_at=utc_now().isoformat())
    write("U_IT", "equipment", "EQ_BLR_22", device)
    for key in ("email", "vpn"):
        source_id = f"it_access_{hire_id}_{key}"
        payload = world.source("U_IT", "it_access", source_id)["payload"]
        payload["state"] = "PROVISIONED"
        write("U_IT", "it_access", source_id, payload)
    write(
        "U_PAYROLL",
        "payroll",
        f"payroll_{hire_id}_main",
        {
            "category": "payroll",
            "profile_created": True,
            "setup_confirmed": True,
            "bank_submitted": True,
            "tax_submitted": True,
        },
    )
    write(
        "U_BENEFITS",
        "benefits",
        f"benefits_{hire_id}_main",
        {"category": "benefits", "state": "ENROLLED"},
    )
    for key, course in (("security", "SECURITY_AWARENESS"), ("coding", "SECURE_CODING")):
        write(
            "U_TRAINING",
            "training",
            f"training_{hire_id}_{key}",
            {"category": "training", "course_id": course, "state": "COMPLETED"},
        )
    assert world.get("U_HR", f"/hires/{hire_id}").json()["onboarding_status"] != "COMPLETED"
    for owner, title in (
        ("U_IT", "Create corporate email"),
        ("U_IT", "Grant VPN"),
        ("U_IT", "Issue Bengaluru office badge"),
        ("U_PAYROLL", "Confirm payroll setup"),
        ("U_BENEFITS", "Complete benefits enrolment"),
        ("U_TRAINING", "security awareness"),
        ("U_TRAINING", "secure coding"),
    ):
        response = world.complete(owner, hire_id, title)
        assert response.status_code == 200, f"{title}: {response.text}"
    final = world.get("U_HR", f"/hires/{hire_id}").json()
    assert final["onboarding_status"] == "COMPLETED"
    assert final["completed_at"] is not None and final["employment_status"] == "ACTIVE"
    assert world.get("U_HR", "/analytics/overview").json()["onboarding_completed"] == 1
    titles = [n["title"] for n in world.get("U_PRIYA", "/notifications").json()["items"]]
    assert "Onboarding complete" in titles
    events = {
        e["event_type"] for e in world.get("U_HR", f"/hires/{hire_id}/history").json()["items"]
    }
    assert {
        "HIRE_CREATED",
        "DOCUMENT_VERIFIED",
        "PROPOSAL_APPROVED",
        "ACTION_SUCCEEDED",
        "ONBOARDING_COMPLETED",
    } <= events


@pytest.mark.parametrize(
    "failure",
    ["MODEL_TIMEOUT", "MODEL_RATE_LIMITED", "MODEL_HTTP_401", "MODEL_HTTP_500", "invalid_json"],
)
def test_ai_failures_leave_human_recovery_available(world, failure):
    reply = "{invalid" if failure == "invalid_json" else ProviderError(failure)
    set_provider_for_tests(Scripted(*([reply] * 8)))
    hire = world.create_hire()
    document = world.upload_fixture(
        "U_PRIYA", hire["id"], "signed_employment", "offer_letter_priya.txt"
    ).json()

    question = "What documents do I need for onboarding?"
    answer = world.post("U_PRIYA", "/assistant/questions", {"question": question}).json()
    assert answer["status"] == "UNAVAILABLE" and answer["claims"] == []
    assert answer["sources"] and answer["suggest_escalation"]
    sent = world.post(
        "U_PRIYA",
        "/assistant/escalations",
        {"question": question, "ai_run_id": answer["ai_run_id"]},
    )
    assert sent.status_code == 201
    resolved = world.post(
        "U_HR",
        f"/assistant/escalations/{sent.json()['id']}/answers",
        {"answer": "Please read the approved onboarding documents guide."},
    )
    assert resolved.status_code == 200 and resolved.json()["state"] == "ANSWERED"

    extraction = world.post("U_HR", f"/documents/{document['id']}/extractions")
    assert extraction.status_code == 503
    assert extraction.json()["error"]["code"] == "AI_UNAVAILABLE"
    assert world.review(document).json()["state"] == "VERIFIED"

    metrics = world.get("U_HR", "/insights/metrics").json()
    assert world.post("U_HR", "/insights/summaries").status_code == 503
    assert world.get("U_HR", "/insights/metrics").json() == metrics
    opened = world.post("U_HR", f"/hires/{hire['id']}/cases", {"message": "Check location."})
    world.work()
    case = world.get("U_HR", f"/cases/{opened.json()['case_id']}").json()
    assert case["state"] == "ESCALATED" and case["proposals"] == []
    assert any(
        item["title"] == "Investigation needs a person"
        for item in world.get("U_HR", "/notifications").json()["items"]
    )
    assert world.get("U_HR", f"/hires/{hire['id']}").json()["location_id"] == "HYD-DEMO"
    with connect() as connection:
        assert connection.execute("SELECT COUNT(*) FROM actions").fetchone()[0] == 0

    proposal = world.post(
        "U_HR",
        f"/hires/{hire['id']}/change-previews",
        {"location_id": "BLR-DEMO", "expected_profile_version": 1},
    ).json()
    decision = world.post("U_HR", f"/proposals/{proposal['id']}/decisions", {"decision": "APPROVE"})
    assert decision.status_code == 200
    world.work()
    assert world.get("U_HR", f"/proposals/{proposal['id']}").json()["action_state"] == "SUCCEEDED"
    assert world.get("U_HR", f"/hires/{hire['id']}").json()["location_id"] == "BLR-DEMO"


def test_the_whole_workflow_runs_with_ai_switched_off(world):
    """Harness promise: no model configured, and every deterministic path still works."""
    hire = world.create_hire()
    document = world.upload_fixture(
        "U_PRIYA", hire["id"], "government_id", "government_id_priya.txt"
    ).json()
    assert world.post("U_HR", f"/documents/{document['id']}/extractions").status_code == 503
    assert world.review(document).json()["state"] == "VERIFIED"
    proposal = world.post(
        "U_IT", f"/hires/{hire['id']}/equipment-requests", {"equipment_record_id": "EQ_HYD_07"}
    ).json()
    world.post("U_IT", f"/proposals/{proposal['id']}/decisions", {"decision": "APPROVE"})
    world.work()
    outcome = world.get("U_IT", f"/proposals/{proposal['id']}").json()["outcome"]
    assert outcome == "LAPTOP_07 reserved; collection pending."
    assert world.get("U_HR", "/analytics/overview").status_code == 200
    assert world.post("U_HR", "/insights/summaries").status_code == 503
    assert world.get("U_HR", "/insights/metrics").status_code == 200
