"""Deterministic checks. A completed task is a claim; only these predicates establish an outcome.

No model output is read here. Missing or unavailable evidence is UNKNOWN, a real mismatch is
BLOCKED, and old receipts are never rewritten.
"""

import json
import sqlite3

from app.shared.contracts import CheckResult, Evidence
from app.shared.util import new_id, now_iso

Outcome = tuple[CheckResult, str, dict, str | None, int | None]


def _latest_document(connection, hire_id: str, category: str):
    return connection.execute(
        "SELECT * FROM documents WHERE hire_id=? AND category=? AND state!='SUPERSEDED' "
        "ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (hire_id, category),
    ).fetchone()


def _sources(connection, hire_id: str, category: str) -> list:
    return connection.execute(
        "SELECT * FROM source_records WHERE hire_id=? AND category=? ORDER BY id",
        (hire_id, category),
    ).fetchall()


def _document_check(connection, hire, category: str) -> Outcome:
    document = _latest_document(connection, hire["id"], category)
    if document is None:
        return CheckResult.UNKNOWN, "DOCUMENT_NOT_SUBMITTED", {}, None, None
    observed = {"state": document["state"], "document_id": document["id"]}
    if document["state"] == "VERIFIED":
        return CheckResult.VERIFIED, "HUMAN_VERIFIED", observed, None, None
    if document["state"] in ("REJECTED", "RESUBMISSION_REQUESTED"):
        return CheckResult.BLOCKED, "DOCUMENT_" + document["state"], observed, None, None
    return CheckResult.UNKNOWN, "AWAITING_HUMAN_REVIEW", observed, None, None


def identity_document_verified(connection, hire) -> Outcome:
    return _document_check(connection, hire, "government_id")


def employment_document_verified(connection, hire) -> Outcome:
    return _document_check(connection, hire, "signed_employment")


def profile_location_confirmed(connection, hire) -> Outcome:
    document = _latest_document(connection, hire["id"], "signed_employment")
    if document is None:
        return CheckResult.UNKNOWN, "NO_EMPLOYMENT_DOCUMENT", {}, None, None
    declared = document["declared_location_id"]
    observed = {
        "profile_location": hire["location_id"],
        "document_location": declared,
        "document_id": document["id"],
    }
    if declared is None:
        return CheckResult.UNKNOWN, "LOCATION_NOT_FOUND_IN_DOCUMENT", observed, None, None
    if declared != hire["location_id"]:
        return CheckResult.BLOCKED, "PROFILE_DOCUMENT_LOCATION_CONFLICT", observed, None, None
    return CheckResult.VERIFIED, "LOCATION_MATCHES", observed, None, None


def device_handover_recorded(connection, hire) -> Outcome:
    records = _sources(connection, hire["id"], "equipment")
    if not records:
        return CheckResult.UNKNOWN, "NO_EQUIPMENT_RECORD", {}, None, None
    record = records[-1]
    payload = json.loads(record["payload_json"])
    observed = {
        "asset_tag": payload["asset_tag"],
        "state": payload["state"],
        "device_location": payload["location_id"],
        "profile_location": hire["location_id"],
    }
    outcome = (record["id"], record["version"])
    if payload["location_id"] != hire["location_id"]:
        return (CheckResult.BLOCKED, "DEVICE_LOCATION_MISMATCH", observed, *outcome)
    if payload["state"] == "HANDED_OVER" and payload.get("handover_at"):
        observed["handover_at"] = payload["handover_at"]
        return (CheckResult.VERIFIED, "HANDOVER_RECORDED", observed, *outcome)
    # A reservation is not a delivery.
    return (CheckResult.UNKNOWN, "RESERVED_COLLECTION_PENDING", observed, *outcome)


def it_access_provisioned(connection, hire) -> Outcome:
    records = _sources(connection, hire["id"], "it_access")
    if not records:
        return CheckResult.UNKNOWN, "NO_ACCESS_RECORDS", {}, None, None
    pending = [
        json.loads(r["payload_json"])["item"]
        for r in records
        if json.loads(r["payload_json"])["state"] != "PROVISIONED"
    ]
    observed = {"pending": ", ".join(pending) or None, "simulated": True}
    if pending:
        return CheckResult.UNKNOWN, "ACCESS_PENDING", observed, None, None
    return CheckResult.VERIFIED, "ACCESS_PROVISIONED_SIMULATED", observed, None, None


def payroll_setup_confirmed(connection, hire) -> Outcome:
    records = _sources(connection, hire["id"], "payroll")
    if not records:
        return CheckResult.UNKNOWN, "NO_PAYROLL_RECORD", {}, None, None
    record = records[0]
    payload = json.loads(record["payload_json"])
    observed = {
        "bank_submitted": payload.get("bank_submitted", False),
        "tax_submitted": payload.get("tax_submitted", False),
        "profile_created": payload["profile_created"],
        "setup_confirmed": payload["setup_confirmed"],
    }
    outcome = (record["id"], record["version"])
    if payload["setup_confirmed"]:
        return (CheckResult.VERIFIED, "PAYROLL_CONFIRMED", observed, *outcome)
    return (CheckResult.UNKNOWN, "PAYROLL_NOT_CONFIRMED", observed, *outcome)


def benefits_resolved(connection, hire) -> Outcome:
    records = _sources(connection, hire["id"], "benefits")
    if not records:
        return CheckResult.UNKNOWN, "NO_BENEFITS_RECORD", {}, None, None
    record = records[0]
    state = json.loads(record["payload_json"])["state"]
    outcome = (record["id"], record["version"])
    if state in ("ENROLLED", "DECLINED"):
        return (CheckResult.VERIFIED, f"BENEFITS_{state}", {"state": state}, *outcome)
    return (CheckResult.UNKNOWN, "BENEFITS_PENDING", {"state": state}, *outcome)


def training_completed(connection, hire) -> Outcome:
    records = _sources(connection, hire["id"], "training")
    if not records:
        return CheckResult.UNKNOWN, "NO_TRAINING_RECORDS", {}, None, None
    payloads = [json.loads(r["payload_json"]) for r in records]
    remaining = [p["course_id"] for p in payloads if p["state"] != "COMPLETED"]
    observed = {"remaining": ", ".join(remaining) or None, "total": len(payloads)}
    if remaining:
        return CheckResult.UNKNOWN, "TRAINING_INCOMPLETE", observed, None, None
    return CheckResult.VERIFIED, "TRAINING_RECORDED_COMPLETE", observed, None, None


def manager_plan_recorded(connection, hire) -> Outcome:
    records = _sources(connection, hire["id"], "manager")
    if not records:
        return CheckResult.UNKNOWN, "NO_MANAGER_PLAN", {}, None, None
    record = records[0]
    payload = json.loads(record["payload_json"])
    return (
        CheckResult.VERIFIED,
        "BUDDY_AND_PLAN_RECORDED",
        {"buddy_user_id": payload["buddy_user_id"]},
        record["id"],
        record["version"],
    )


CHECKS = {
    "identity_document_verified": identity_document_verified,
    "employment_document_verified": employment_document_verified,
    "profile_location_confirmed": profile_location_confirmed,
    "device_handover_recorded": device_handover_recorded,
    "it_access_provisioned": it_access_provisioned,
    "payroll_setup_confirmed": payroll_setup_confirmed,
    "benefits_resolved": benefits_resolved,
    "training_completed": training_completed,
    "manager_plan_recorded": manager_plan_recorded,
}


def to_evidence(row) -> Evidence:
    return Evidence(
        id=row["id"],
        hire_id=row["hire_id"],
        case_id=row["case_id"],
        check_type=row["check_type"],
        source_record_id=row["source_record_id"],
        source_version=row["source_version"],
        profile_version=row["profile_version"],
        policy_id=row["policy_id"],
        policy_version=row["policy_version"],
        checked_at=row["checked_at"],
        expires_at=row["expires_at"],
        result=row["result"],
        reason_code=row["reason_code"],
        observed=json.loads(row["observed_json"]),
    )


def latest_evidence(connection: sqlite3.Connection, hire_id: str) -> list[Evidence]:
    rows = connection.execute(
        "SELECT e.* FROM evidence e JOIN ("
        "  SELECT check_type, MAX(rowid) AS newest FROM evidence WHERE hire_id=? "
        "  GROUP BY check_type"
        ") latest ON latest.newest = e.rowid ORDER BY e.check_type",
        (hire_id,),
    ).fetchall()
    return [to_evidence(row) for row in rows]


def _applicable_checks(connection, hire_id: str) -> dict[str, tuple[str, int]]:
    rows = connection.execute(
        "SELECT DISTINCT check_type, policy_id, policy_version FROM tasks "
        "WHERE hire_id=? AND check_type IS NOT NULL AND work_state!='CANCELLED'",
        (hire_id,),
    ).fetchall()
    return {row["check_type"]: (row["policy_id"], row["policy_version"]) for row in rows}


def check_hire(connection: sqlite3.Connection, hire_id: str) -> list[Evidence]:
    """Evaluate every applicable check. A receipt is appended only when the answer changes."""
    hire = connection.execute("SELECT * FROM hires WHERE id=?", (hire_id,)).fetchone()
    if hire is None:
        return []
    current = {item.check_type: item for item in latest_evidence(connection, hire_id)}
    for check_type, (policy_id, policy_version) in _applicable_checks(connection, hire_id).items():
        result, reason, observed, source_id, source_version = CHECKS[check_type](connection, hire)
        previous = current.get(check_type)
        if (
            previous
            and previous.result == result
            and previous.reason_code == reason
            and previous.source_version == source_version
            and previous.profile_version == hire["profile_version"]
            and previous.policy_id == policy_id
            and previous.policy_version == policy_version
            and previous.observed == observed
        ):
            continue
        connection.execute(
            "INSERT INTO evidence (id, hire_id, check_type, source_record_id, source_version, "
            "profile_version, policy_id, policy_version, result, reason_code, observed_json, "
            "checked_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                new_id("EV"),
                hire_id,
                check_type,
                source_id,
                source_version,
                hire["profile_version"],
                policy_id,
                policy_version,
                result.value,
                reason,
                json.dumps(observed),
                now_iso(),
            ),
        )
    applicable = _applicable_checks(connection, hire_id)
    return [e for e in latest_evidence(connection, hire_id) if e.check_type in applicable]
