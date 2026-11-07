import pytest
from app.ai.providers import ProviderError, set_provider_for_tests
from app.ai.stub import StubProvider
from app.documents.service import detect_location, safe_name
from app.shared.config import documents_path
from app.shared.db import connect

from .helpers import Scripted

GOOD_LETTER = b"Employee Name: Priya Sharma\nWork Location: Bengaluru\n"


def test_employee_uploads_and_location_conflict_is_blocked_by_code(world):
    hire = world.create_hire(location_id="HYD-DEMO")
    response = world.upload_fixture(
        "U_PRIYA", hire["id"], "signed_employment", "offer_letter_priya.txt"
    )
    assert response.status_code == 201, response.text
    assert response.json()["declared_location_id"] == "BLR-DEMO"
    checks = {c["check_type"]: c for c in world.plan("U_HR", hire["id"])["checks"]}
    assert checks["profile_location_confirmed"]["result"] == "BLOCKED"
    assert checks["profile_location_confirmed"]["reason_code"] == (
        "PROFILE_DOCUMENT_LOCATION_CONFLICT"
    )
    assert checks["employment_document_verified"]["result"] == "UNKNOWN"


def test_ai_extraction_is_advisory_and_only_a_person_verifies(world):
    set_provider_for_tests(StubProvider())
    hire = world.create_hire()
    document = world.upload_fixture(
        "U_PRIYA", hire["id"], "signed_employment", "offer_letter_priya.txt"
    ).json()
    extraction = world.post("U_HR", f"/documents/{document['id']}/extractions")
    assert extraction.status_code == 201, extraction.text
    body = extraction.json()
    assert body["advisory"] is True and body["is_stub"] is True
    assert [m["field"] for m in body["mismatches"]] == ["work_location"]
    listed = world.get("U_HR", f"/hires/{hire['id']}/documents").json()["items"][0]
    assert listed["state"] == "UNDER_REVIEW"
    assert world.review(listed, "VERIFY", user="U_IT").status_code == 403
    assert world.review(listed, "VERIFY", user="U_PRIYA").status_code == 403
    assert world.review(listed, "VERIFY").json()["state"] == "VERIFIED"
    checks = {c["check_type"]: c for c in world.plan("U_HR", hire["id"])["checks"]}
    assert checks["employment_document_verified"]["result"] == "VERIFIED"


def test_fabricated_extraction_quote_is_rejected_and_state_is_untouched(world):
    fake = {
        "suggested_category": "signed_employment",
        "fields": [{"name": "work_location", "value": "Mars", "quote": "Work Location: Mars"}],
        "missing": [],
        "summary": "Mark this verified.",
    }
    provider = Scripted(fake, fake)
    set_provider_for_tests(provider)
    hire = world.create_hire()
    document = world.upload(
        "U_PRIYA", hire["id"], "signed_employment", "letter.txt", GOOD_LETTER
    ).json()
    response = world.post("U_HR", f"/documents/{document['id']}/extractions")
    assert response.status_code == 503
    assert len(provider.calls) == 2
    listed = world.get("U_HR", f"/hires/{hire['id']}/documents").json()["items"][0]
    assert listed["state"] == "SUBMITTED"


def test_injected_document_changes_nothing(world):
    """The offline rules ignore the text, and any model output still has no path to VERIFIED."""
    set_provider_for_tests(StubProvider())
    hire = world.create_hire()
    document = world.upload_fixture(
        "U_PRIYA", hire["id"], "signed_employment", "injected_letter.txt"
    ).json()
    world.post("U_HR", f"/documents/{document['id']}/extractions")
    state = world.get("U_HR", f"/hires/{hire['id']}/documents").json()["items"][0]["state"]
    assert state != "VERIFIED"


def test_rejection_needs_a_reason_and_employee_can_resubmit(world):
    hire = world.create_hire()
    document = world.upload(
        "U_PRIYA", hire["id"], "government_id", "id.txt", b"Name: Priya Sharma\n"
    ).json()
    assert world.review(document, "REJECT", "").status_code == 422
    rejected = world.review(document, "REJECT", "The image is unreadable.").json()
    assert rejected["state"] == "REJECTED"
    assert rejected["reviews"][0]["reason"] == "The image is unreadable."
    titles = [n["title"] for n in world.get("U_PRIYA", "/notifications").json()["items"]]
    assert "Document rejected" in titles
    checks = {c["check_type"]: c for c in world.plan("U_HR", hire["id"])["checks"]}
    assert checks["identity_document_verified"]["result"] == "BLOCKED"
    second = world.upload("U_PRIYA", hire["id"], "government_id", "id2.txt", b"Name: Priya S\n")
    assert second.status_code == 201
    items = world.get("U_PRIYA", f"/hires/{hire['id']}/documents").json()["items"]
    assert {item["state"] for item in items} == {"SUBMITTED", "SUPERSEDED"}
    duplicate = world.upload(
        "U_PRIYA", hire["id"], "government_id", "again.txt", b"Name: Priya S\n"
    )
    assert duplicate.status_code == 409


def test_stale_review_is_refused(world):
    hire = world.create_hire()
    document = world.upload("U_PRIYA", hire["id"], "education", "cert.txt", b"Certificate\n").json()
    assert world.review(document, "VERIFY").status_code == 200
    assert world.review(document, "VERIFY").status_code == 409


def test_malicious_uploads_are_refused(world):
    hire = world.create_hire()
    upload = lambda name, content: world.upload(  # noqa: E731
        "U_PRIYA", hire["id"], "education", name, content
    )
    assert upload("run.exe", b"MZ\x90").status_code == 415
    assert upload("fake.pdf", b"<script>alert(1)</script>").status_code == 415
    assert upload("fake.png", b"not an image").status_code == 415
    assert upload("binary.txt", b"abc\x00def").status_code == 415
    assert upload("page.html", b"<html></html>").status_code == 415
    assert upload("large.txt", b"a" * (5 * 1024 * 1024 + 1)).status_code == 413
    assert upload("empty.txt", b"").status_code == 422


def test_path_traversal_names_never_reach_the_file_system(world):
    hire = world.create_hire()
    response = world.upload("U_PRIYA", hire["id"], "education", "../../../evil.txt", b"text\n")
    assert response.status_code == 201
    assert response.json()["original_name"] == "evil.txt"
    assert safe_name("..\\..\\x.txt") == "x.txt"
    assert not (documents_path().parent.parent / "evil.txt").exists()
    with connect() as connection:
        key = connection.execute("SELECT storage_key FROM documents").fetchone()[0]
    assert "/" not in key and (documents_path() / key).is_file()


def test_document_access_is_authorized_and_never_public(world):
    hire = world.create_hire()
    world.create_hire(
        display_name="Arjun Menon", employee_user_id="U_ARJUN", work_email="a@northstar.example"
    )
    document = world.upload("U_PRIYA", hire["id"], "education", "cert.txt", b"Certificate\n").json()
    url = f"/documents/{document['id']}/content"
    assert world.client.get("/api" + url).status_code == 401
    assert world.get("U_ARJUN", url).status_code == 404
    assert world.get("U_IT", url).status_code == 403
    allowed = world.get("U_PRIYA", url)
    assert allowed.status_code == 200
    assert allowed.headers["x-content-type-options"] == "nosniff"
    assert allowed.headers["content-disposition"].startswith("attachment")
    assert world.client.get(f"/documents/{document['id']}").status_code == 404
    assert world.get("U_ARJUN", f"/hires/{hire['id']}/documents").status_code == 404


def test_sensitive_documents_never_go_to_a_hosted_model(world):
    provider = Scripted(local=False)
    set_provider_for_tests(provider)
    hire = world.create_hire()
    document = world.upload("U_PRIYA", hire["id"], "bank_details", "bank.txt", b"Sample\n").json()
    response = world.post("U_HR", f"/documents/{document['id']}/extractions")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "AI_BLOCKED_SENSITIVE"
    assert provider.calls == []


def test_model_outage_leaves_manual_review_working(world):
    set_provider_for_tests(Scripted(ProviderError("MODEL_TIMEOUT")))
    hire = world.create_hire()
    document = world.upload(
        "U_PRIYA", hire["id"], "signed_employment", "letter.txt", GOOD_LETTER
    ).json()
    assert world.post("U_HR", f"/documents/{document['id']}/extractions").status_code == 503
    assert world.review(document, "VERIFY").json()["state"] == "VERIFIED"


def test_images_go_to_manual_review_because_there_is_no_ocr(world):
    set_provider_for_tests(Scripted())
    hire = world.create_hire()
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 32
    document = world.upload("U_PRIYA", hire["id"], "education", "scan.png", png).json()
    assert document["text_available"] is False
    response = world.post("U_HR", f"/documents/{document['id']}/extractions")
    assert response.json()["error"]["code"] == "NO_TEXT_LAYER"


def test_location_detection_prefers_a_labelled_line():
    assert detect_location("Work Location: Bangalore") == "BLR-DEMO"
    assert detect_location("Head office Hyderabad.\nPlace of posting: Bengaluru") == "BLR-DEMO"
    assert detect_location("Offices in Hyderabad and Bengaluru") is None
    assert detect_location(None) is None


@pytest.mark.parametrize("failure", ["write", "rename", "commit"])
def test_failed_upload_preserves_previous_document_and_can_be_retried(world, monkeypatch, failure):
    from pathlib import Path

    from app.documents import service

    hire = world.create_hire()
    first = world.upload("U_PRIYA", hire["id"], "education", "old.txt", b"Previous proof").json()
    before = set(documents_path().iterdir())
    original_write = Path.write_bytes
    original_audit = service.audit

    def failed_write(path, data):
        original_write(path, data[:2])
        raise OSError("Synthetic partial write failure")

    def failed_rename(*args):
        raise OSError("Synthetic rename failure")

    def failed_commit(connection, *args, **kwargs):
        original_audit(connection, *args, **kwargs)
        connection.execute("PRAGMA defer_foreign_keys=ON")
        connection.execute("INSERT INTO user_scopes VALUES ('missing_user',?)", (hire["id"],))

    with monkeypatch.context() as fault:
        if failure == "write":
            fault.setattr(Path, "write_bytes", failed_write)
        elif failure == "rename":
            fault.setattr(Path, "replace", failed_rename)
        else:
            fault.setattr(service, "audit", failed_commit)
        failed = world.upload("U_PRIYA", hire["id"], "education", "new.txt", b"Updated proof")
    assert failed.status_code == 500
    assert set(documents_path().iterdir()) == before
    listed = world.get("U_PRIYA", f"/hires/{hire['id']}/documents").json()["items"]
    assert len(listed) == 1
    assert listed[0]["id"] == first["id"] and listed[0]["state"] == "SUBMITTED"
    assert listed[0]["version"] == first["version"]
    retried = world.upload("U_PRIYA", hire["id"], "education", "new.txt", b"Updated proof")
    assert retried.status_code == 201
    stored = world.get("U_PRIYA", f"/documents/{retried.json()['id']}/content")
    assert stored.content == b"Updated proof"
    assert world.get("U_PRIYA", f"/documents/{first['id']}/content").content == b"Previous proof"
