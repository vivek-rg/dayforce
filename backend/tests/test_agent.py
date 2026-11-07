import json
from datetime import date, timedelta

import pytest
from app.agent.worker import process_pending_work, reconcile_after_restart
from app.ai import providers
from app.ai.providers import HostedProvider, OllamaProvider, ProviderError, set_provider_for_tests
from app.ai.stub import StubProvider
from app.shared import config
from app.shared.db import connect

from .helpers import Scripted

READ_DOCS = {
    "next_step": {
        "step": "read",
        "tool": "get_document_evidence",
        "reason_summary": "Read documents.",
    }
}


def open_case(world, hire_id):
    response = world.post("U_HR", f"/hires/{hire_id}/cases", {"message": "Please investigate."})
    assert response.status_code == 202, response.text
    return response.json()["case_id"]


def case(world, case_id, user="U_HR"):
    return world.get(user, f"/cases/{case_id}").json()


def conflict_hire(world):
    hire = world.create_hire(location_id="HYD-DEMO")
    world.upload_fixture("U_PRIYA", hire["id"], "signed_employment", "offer_letter_priya.txt")
    return hire


def test_investigation_pauses_durably_and_resumes_after_restart(world):
    set_provider_for_tests(StubProvider())
    hire = conflict_hire(world)
    case_id = open_case(world, hire["id"])
    world.work()
    paused = case(world, case_id)
    assert paused["state"] == "WAITING_HUMAN"
    assert paused["model_calls"] == 3 and paused["tool_calls"] == 2
    question = paused["questions"][0]
    assert "BLR-DEMO" in question["text"]
    assert question["recipient_user_id"] == "U_HR"
    assert world.get("U_HR", "/questions").json()["items"][0]["id"] == question["id"]

    # Simulate a restart: nothing in memory matters and a crashed run is reconciled.
    set_provider_for_tests(None)
    reconcile_after_restart()
    set_provider_for_tests(StubProvider())
    assert process_pending_work() == 0
    assert case(world, case_id)["state"] == "WAITING_HUMAN"

    assert (
        world.post("U_IT", f"/questions/{question['id']}/responses", {"answer": "x"}).status_code
        == 403
    )
    answer = {"answer": "Bengaluru is correct."}
    response = world.post("U_HR", f"/questions/{question['id']}/responses", answer)
    assert response.status_code == 202
    # An answer is not an approval and does not change official records.
    assert world.get("U_HR", f"/hires/{hire['id']}").json()["location_id"] == "HYD-DEMO"
    retry = world.post("U_HR", f"/questions/{question['id']}/responses", answer)
    assert retry.json() == response.json()
    other = world.post("U_HR", f"/questions/{question['id']}/responses", {"answer": "No."})
    assert other.status_code == 409
    world.work()
    waiting = case(world, case_id)
    assert waiting["state"] == "WAITING_APPROVAL"
    proposal = waiting["proposals"][0]
    assert proposal["payload"] == {"action_type": "CHANGE_WORK_LOCATION", "location_id": "BLR-DEMO"}
    assert proposal["reviewer_role"] == "HR"
    assert world.get("U_HR", f"/hires/{hire['id']}").json()["location_id"] == "HYD-DEMO"


def test_model_cannot_choose_the_reviewer_or_arbitrary_tools(world):
    hire = conflict_hire(world)
    bad = [
        {"next_step": {"step": "read", "tool": "execute_sql", "reason_summary": "Dump it."}},
        {
            "next_step": {
                "step": "read",
                "tool": "get_hire_context",
                "hire_id": "OTHER",
                "reason_summary": "Other hire.",
            }
        },
    ]
    set_provider_for_tests(Scripted(*bad))
    case_id = open_case(world, hire["id"])
    world.work()
    assert case(world, case_id)["state"] == "ESCALATED"
    with connect() as connection:
        assert connection.execute("SELECT COUNT(*) FROM case_steps").fetchone()[0] == 0


def test_model_proposal_with_foreign_evidence_is_refused(world):
    hire = conflict_hire(world)
    other = world.create_hire(
        display_name="Ravi Kumar", employee_user_id="U_RAVI", work_email="r@northstar.example"
    )
    with connect() as connection:
        foreign = connection.execute(
            "SELECT id FROM evidence WHERE hire_id=? LIMIT 1", (other["id"],)
        ).fetchone()[0]
    propose = {
        "next_step": {
            "step": "propose",
            "payload": {"action_type": "CHANGE_WORK_LOCATION", "location_id": "BLR-DEMO"},
            "evidence_ids": [foreign],
            "reason_summary": "Use their evidence.",
        }
    }
    finish = {"next_step": {"step": "escalate", "reason_summary": "Stop.", "evidence_ids": []}}
    set_provider_for_tests(Scripted(propose, finish))
    case_id = open_case(world, hire["id"])
    world.work()
    current = case(world, case_id)
    assert current["proposals"] == []
    assert current["state"] == "ESCALATED"


def test_model_budget_is_enforced_and_persisted(world, monkeypatch):
    monkeypatch.setenv("MAX_MODEL_CALLS", "3")
    set_provider_for_tests(Scripted(*[READ_DOCS] * 10))
    hire = conflict_hire(world)
    case_id = open_case(world, hire["id"])
    world.work()
    current = case(world, case_id)
    assert current["state"] == "ESCALATED"
    assert current["model_calls"] == 3


def test_read_budget_is_enforced(world, monkeypatch):
    monkeypatch.setenv("MAX_TOOL_CALLS", "1")
    set_provider_for_tests(Scripted(READ_DOCS, READ_DOCS))
    hire = conflict_hire(world)
    case_id = open_case(world, hire["id"])
    world.work()
    current = case(world, case_id)
    assert current["state"] == "ESCALATED" and current["tool_calls"] == 1


def test_model_outage_escalates_and_workflow_continues(world):
    set_provider_for_tests(Scripted(ProviderError("MODEL_TIMEOUT")))
    hire = conflict_hire(world)
    case_id = open_case(world, hire["id"])
    world.work()
    assert case(world, case_id)["state"] == "ESCALATED"
    titles = [n["title"] for n in world.get("U_HR", "/notifications").json()["items"]]
    assert "Investigation needs a person" in titles
    assert world.complete("U_PRIYA", hire["id"], "Submit government ID").status_code == 200


def test_scope_is_rechecked_when_a_run_resumes(world):
    set_provider_for_tests(StubProvider())
    hire = conflict_hire(world)
    case_id = open_case(world, hire["id"])
    world.work()
    question = case(world, case_id)["questions"][0]
    world.post("U_HR", f"/questions/{question['id']}/responses", {"answer": "Bengaluru."})
    with connect() as connection:
        connection.execute(
            "DELETE FROM user_scopes WHERE user_id='U_HR' AND hire_id=?", (hire["id"],)
        )
    world.work()
    with connect() as connection:
        state = connection.execute("SELECT state FROM cases WHERE id=?", (case_id,)).fetchone()[0]
    assert state == "ESCALATED"


def test_transcript_is_not_exposed_through_the_case_api(world):
    set_provider_for_tests(StubProvider())
    hire = conflict_hire(world)
    case_id = open_case(world, hire["id"])
    world.work()
    body = case(world, case_id)
    assert "Offer of Employment" not in json.dumps(body)
    assert "steps" not in body
    with connect() as connection:
        runs = connection.execute("SELECT * FROM ai_runs WHERE case_id=?", (case_id,)).fetchall()
    assert runs
    assert "Offer of Employment" not in json.dumps([dict(r) for r in runs])


def test_case_routes_are_scoped(world):
    set_provider_for_tests(StubProvider())
    hire = conflict_hire(world)
    case_id = open_case(world, hire["id"])
    assert world.get("U_MANAGER2", f"/cases/{case_id}").status_code == 404
    assert world.post("U_IT", f"/hires/{hire['id']}/cases", {"message": "x"}).status_code == 403


def test_crash_during_work_is_reconciled_and_retried(world):
    set_provider_for_tests(StubProvider())
    hire = conflict_hire(world)
    case_id = open_case(world, hire["id"])
    with connect() as connection:
        connection.execute("UPDATE work_items SET state='RUNNING', attempts=1")
    assert reconcile_after_restart() == 1
    world.work()
    assert case(world, case_id)["state"] == "WAITING_HUMAN"
    with connect() as connection:
        connection.execute("UPDATE work_items SET state='RUNNING', attempts=3")
    reconcile_after_restart()
    assert case(world, case_id)["state"] == "ESCALATED"


def test_insights_are_sql_first_and_summary_is_validated(world):
    hire = world.create_hire(start_date=(date.today() + timedelta(days=30)).isoformat())
    with connect() as connection:
        connection.execute(
            "UPDATE tasks SET due_date=? WHERE hire_id=? AND logical_key='MANAGER_INTRO'",
            ((date.today() - timedelta(days=1)).isoformat(), hire["id"]),
        )
    metrics = world.get("U_HR", "/insights/metrics").json()["metrics"]
    overdue = next(metric for metric in metrics if metric["id"] == "overdue")
    assert overdue["value"] == 1
    set_provider_for_tests(StubProvider())
    summary = world.post("U_HR", "/insights/summaries")
    assert summary.status_code == 200, summary.text
    assert summary.json()["advisory"] is True
    assert overdue["evidence"][0]["ref"] in json.dumps(summary.json()["recommendations"])
    invented = {"summary": "There are 500 overdue tasks.", "recommendations": []}
    set_provider_for_tests(Scripted(invented, invented))
    assert world.post("U_HR", "/insights/summaries").status_code == 503
    assert world.get("U_HR", "/insights/metrics").status_code == 200
    assert world.get("U_PRIYA", "/insights/metrics").status_code == 403


def test_transports_send_no_fallback_and_sanitize_errors(monkeypatch):
    class Response:
        status_code = 500
        text = "secret provider body"

        def json(self):
            return {}

    monkeypatch.setattr(providers.httpx, "post", lambda *a, **k: Response())
    for provider in (
        OllamaProvider("m", "http://127.0.0.1:11434"),
        HostedProvider("m", "https://example.invalid/v1", "KEY"),
    ):
        try:
            provider.generate("x", [{"role": "system", "content": "s"}], {}, 1, 10)
            raise AssertionError("expected failure")
        except ProviderError as exc:
            assert str(exc) == "MODEL_HTTP_500"


def test_transports_parse_a_good_reply(monkeypatch):
    captured = {}

    class Response:
        status_code = 200

        def json(self):
            return {
                "choices": [{"message": {"content": '{"ok": true}'}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 4},
            }

    def fake(url, **kwargs):
        captured.update(kwargs, url=url)
        return Response()

    monkeypatch.setattr(providers.httpx, "post", fake)
    reply = HostedProvider("m", "https://example.invalid/v1", "KEY").generate(
        "x", [{"role": "system", "content": "s"}], {"type": "object"}, 1, 10
    )
    assert reply.text == '{"ok": true}' and reply.output_tokens == 4
    assert captured["follow_redirects"] is False
    assert captured["url"].endswith("/chat/completions")


def test_rate_limit_waits_once_for_a_short_delay_then_gives_up(monkeypatch):
    class Limited:
        status_code = 429
        headers = {"retry-after": "3"}

    class Good:
        status_code = 200
        headers = {}

        def json(self):
            return {"choices": [{"message": {"content": "{}"}}], "usage": {}}

    waits = []
    monkeypatch.setattr(providers.time, "sleep", waits.append)
    replies = [Limited(), Good()]
    monkeypatch.setattr(providers.httpx, "post", lambda *a, **k: replies.pop(0))
    provider = HostedProvider("m", "https://example.invalid/v1", "KEY")
    messages = [{"role": "system", "content": "s"}]
    assert provider.generate("x", messages, {}, 1, 10).text == "{}"
    assert waits == [3.0]

    replies = [Limited(), Limited()]
    try:
        provider.generate("x", messages, {}, 1, 10)
        raise AssertionError("expected failure")
    except ProviderError as exc:
        assert str(exc) == "MODEL_RATE_LIMITED"

    class LongWait(Limited):
        headers = {"retry-after": "3600"}

    replies = [LongWait()]
    waits.clear()
    try:
        provider.generate("x", messages, {}, 1, 10)
        raise AssertionError("expected failure")
    except ProviderError:
        assert waits == []


def test_malformed_json_reported_as_400_goes_to_repair(monkeypatch):
    class Invalid:
        status_code = 400
        headers = {}

        def json(self):
            return {"error": {"code": "json_validate_failed", "failed_generation": "{oops"}}

    class OtherError(Invalid):
        def json(self):
            return {"error": {"code": "invalid_api_key"}}

    provider = HostedProvider("m", "https://example.invalid/v1", "KEY")
    messages = [{"role": "system", "content": "s"}]
    monkeypatch.setattr(providers.httpx, "post", lambda *a, **k: Invalid())
    assert provider.generate("x", messages, {}, 1, 10).text == "{oops"
    monkeypatch.setattr(providers.httpx, "post", lambda *a, **k: OtherError())
    try:
        provider.generate("x", messages, {}, 1, 10)
        raise AssertionError("expected failure")
    except ProviderError as exc:
        assert str(exc) == "MODEL_HTTP_400"


def test_pasted_key_works_without_a_restart(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_API_KEY=\n", encoding="utf-8")
    monkeypatch.setattr(config, "ENV_FILE", env_file)
    monkeypatch.setattr(config, "_FILE_AT_START", {"LLM_API_KEY": ""})
    monkeypatch.setenv("LLM_API_KEY", "")
    set_provider_for_tests(None)
    monkeypatch.setenv("LLM_PROVIDER", "hosted")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.invalid/v1")
    assert providers.current_provider().name == "none"
    env_file.write_text("LLM_API_KEY=first-key\n", encoding="utf-8")
    assert providers.current_provider().api_key == "first-key"
    env_file.write_text("LLM_API_KEY= second-key \n", encoding="utf-8")
    assert providers.current_provider().api_key == "second-key"


def test_status_tells_the_person_what_to_do_about_a_key(world):
    assert "Paste a Groq key" in world.get("U_HR", "/health/ai").json()["detail"]
    set_provider_for_tests(Scripted(ProviderError("MODEL_RATE_LIMITED")))
    world.post("U_PRIYA", "/assistant/questions", {"question": "How do I request a laptop?"})
    assert "paste another key" in world.get("U_HR", "/health/ai").json()["detail"]
    set_provider_for_tests(Scripted(ProviderError("MODEL_HTTP_401")))
    world.post("U_PRIYA", "/assistant/questions", {"question": "How do I request a laptop?"})
    assert "key was rejected" in world.get("U_HR", "/health/ai").json()["detail"]


def test_insecure_hosted_url_disables_ai(monkeypatch):
    set_provider_for_tests(None)
    monkeypatch.setenv("LLM_PROVIDER", "hosted")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.setenv("LLM_API_KEY", "k")
    monkeypatch.setenv("LLM_BASE_URL", "http://evil.example/v1")
    assert providers.current_provider().name == "none"
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.invalid/v1")
    assert providers.current_provider().name == "hosted"


@pytest.mark.parametrize(
    "viewer", ["U_PRIYA", "U_MANAGER", "U_IT", "U_PAYROLL", "U_BENEFITS", "U_TRAINING"]
)
def test_case_discussion_is_private_for_other_roles(world, viewer):
    from app.shared.util import audit

    hire = world.create_hire()
    marker = "HR_ONLY_SYNTHETIC_DISCUSSION"
    opened = world.post("U_HR", f"/hires/{hire['id']}/cases", {"message": marker})
    case_id = opened.json()["case_id"]
    with connect() as connection:
        connection.execute(
            "INSERT INTO questions (id, case_id, dedupe_key, recipient_user_id, text, state, "
            "answer, answered_by) VALUES ('Q_PRIVATE',?,'private','U_HR',?,'ANSWERED',?,'U_HR')",
            (case_id, marker, marker),
        )
        connection.execute(
            "INSERT INTO questions (id, case_id, dedupe_key, recipient_user_id, text, state) "
            "VALUES ('Q_OWN',?,'own',?,'Please confirm your part.','PENDING')",
            (case_id, viewer),
        )
        audit(connection, hire["id"], "CASE_RESOLVED", marker, "U_HR", case_id)
    hr_view = world.get("U_HR", f"/cases/{case_id}")
    assert marker in hr_view.text and len(hr_view.json()["questions"]) == 2
    response = world.get(viewer, f"/cases/{case_id}")
    assert response.status_code == 200
    assert marker not in response.text
    assert [q["id"] for q in response.json()["questions"]] == ["Q_OWN"]
    assert marker not in world.get(viewer, f"/hires/{hire['id']}/history").text
    if viewer == "U_MANAGER":
        assert marker not in world.get(viewer, f"/hires/{hire['id']}/cases").text
    if viewer == "U_IT":
        assert {e["check_type"] for e in response.json()["evidence"]} <= {
            "device_handover_recorded",
            "it_access_provisioned",
        }
    assert world.get(viewer, "/questions").json()["items"][0]["id"] == "Q_OWN"
    assert (
        world.post(viewer, "/questions/Q_OWN/responses", {"answer": "Confirmed."}).status_code
        == 202
    )
    assert world.get("U_MANAGER2", f"/cases/{case_id}").status_code == 404


def test_question_list_rechecks_hire_scope(world):
    hire = world.create_hire()
    case_id = open_case(world, hire["id"])
    with connect() as connection:
        connection.execute(
            "INSERT INTO questions (id, case_id, dedupe_key, recipient_user_id, text, state) "
            "VALUES ('Q_REVOKED',?,'revoked','U_HR','Private question.','PENDING')",
            (case_id,),
        )
        connection.execute(
            "DELETE FROM user_scopes WHERE user_id='U_HR' AND hire_id=?", (hire["id"],)
        )
    assert world.get("U_HR", "/questions").json()["items"] == []
    assert world.post("U_HR", "/questions/Q_REVOKED/responses", {"answer": "x"}).status_code == 404


@pytest.mark.parametrize("kind", ["hosted", "ollama"])
@pytest.mark.parametrize(
    "malformation",
    [
        "non_json",
        "not_object",
        "missing_content",
        "non_text",
        "bad_usage",
        "negative_tokens",
        "boolean_tokens",
    ],
)
def test_provider_envelopes_are_validated(monkeypatch, kind, malformation):
    provider = (
        HostedProvider("m", "https://example.invalid/v1", "SYNTHETIC_KEY")
        if kind == "hosted"
        else OllamaProvider("m", "http://127.0.0.1:11434")
    )
    body = (
        {"choices": [{"message": {"content": "{}"}}], "usage": {"prompt_tokens": 1}}
        if kind == "hosted"
        else {"message": {"content": "{}"}, "prompt_eval_count": 1}
    )
    if malformation == "not_object":
        body = []
    elif malformation == "missing_content":
        body = {}
    elif malformation == "non_text":
        message = body["choices"][0]["message"] if kind == "hosted" else body["message"]
        message["content"] = ["SECRET_PROVIDER_BODY"]
    elif malformation in ("bad_usage", "negative_tokens", "boolean_tokens"):
        value = {
            "bad_usage": "SECRET_PROVIDER_BODY",
            "negative_tokens": -1,
            "boolean_tokens": True,
        }[malformation]
        if kind == "hosted":
            body["usage"]["prompt_tokens"] = value
        else:
            body["prompt_eval_count"] = value
    response = (
        providers.httpx.Response(200, content=b"SECRET_PROVIDER_BODY")
        if malformation == "non_json"
        else providers.httpx.Response(200, json=body)
    )
    monkeypatch.setattr(providers.httpx, "post", lambda *a, **k: response)
    with pytest.raises(ProviderError, match="^MODEL_INVALID_RESPONSE$"):
        provider.generate("assistant.answer", [{"role": "system", "content": "s"}], {}, 1, 10)


def test_bad_provider_envelope_keeps_sources_and_records_failure(world, monkeypatch):
    set_provider_for_tests(HostedProvider("m", "https://example.invalid/v1", "SYNTHETIC_KEY"))
    monkeypatch.setattr(
        providers.httpx, "post", lambda *a, **k: providers.httpx.Response(200, json={"choices": []})
    )
    response = world.post(
        "U_PRIYA", "/assistant/questions", {"question": "How do I request a laptop?"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "UNAVAILABLE" and response.json()["sources"]
    with connect() as connection:
        run = connection.execute("SELECT * FROM ai_runs ORDER BY rowid DESC LIMIT 1").fetchone()
    assert run["status"] == "UNAVAILABLE" and run["failure_reason"] == "MODEL_INVALID_RESPONSE"
    assert "SYNTHETIC_KEY" not in response.text
