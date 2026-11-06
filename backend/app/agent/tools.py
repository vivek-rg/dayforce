"""Allowlisted reads. The server binds hire and case; the model supplies no IDs, URLs or SQL."""

import json

from app.auth.permissions import SENSITIVE_DOCUMENTS
from app.auth.service import load_user
from app.documents.service import extract_text, read_stored
from app.evidence.service import check_hire
from app.planning.service import get_hire_row, load_tasks
from app.shared.contracts import InvestigationContext, ToolObservation
from app.shared.db import connect


class ScopeLost(Exception):
    """The person who opened the case no longer has access. The run must stop."""


def _hire_context(connection, hire, context):
    return ToolObservation(
        evidence=[],
        facts={
            "profile_location": hire["location_id"],
            "work_mode": hire["work_mode"],
            "worker_type": hire["worker_type"],
            "role": hire["role"],
            "start_date": hire["start_date"],
            "profile_version": hire["profile_version"],
        },
    )


def _tasks(connection, hire, context):
    tasks = load_tasks(connection, hire["id"])
    facts = {
        f"task_{task.category.value}_{index}": (
            f"{task.title}: {task.display_status.value}, evidence "
            f"{task.evidence_result.value if task.evidence_result else 'NONE'}"
        )
        for index, task in enumerate(tasks)
    }
    return ToolObservation(evidence=[], facts=facts)


def _documents(connection, hire, context):
    rows = connection.execute(
        "SELECT * FROM documents WHERE hire_id=? AND state!='SUPERSEDED' ORDER BY created_at",
        (hire["id"],),
    ).fetchall()
    facts = {"profile_location": hire["location_id"], "documents_on_file": len(rows)}
    untrusted = []
    for row in rows:
        facts[f"document_{row['category']}_state"] = row["state"]
        if row["category"] == "signed_employment" and row["declared_location_id"]:
            facts["document_location"] = row["declared_location_id"]
        if row["category"] not in SENSITIVE_DOCUMENTS:
            text = extract_text(row["mime_type"], read_stored(row))
            if text:
                untrusted.append(f"[{row['category']}]\n{text}")
    evidence = [
        item
        for item in check_hire(connection, hire["id"])
        if "document" in item.check_type or item.check_type == "profile_location_confirmed"
    ]
    return ToolObservation(
        evidence=evidence, facts=facts, untrusted_text="\n\n".join(untrusted)[:12000] or None
    )


def _policy(connection, hire, context):
    row = connection.execute(
        "SELECT p.sections_json, p.id, p.version FROM policies p "
        "JOIN tasks t ON t.policy_id=p.id AND t.policy_version=p.version WHERE t.hire_id=? LIMIT 1",
        (hire["id"],),
    ).fetchone()
    sections = json.loads(row["sections_json"]) if row else []
    return ToolObservation(
        evidence=[],
        facts={f"policy_{s['id']}": s["text"][:300] for s in sections},
    )


def _equipment(connection, hire, context):
    records = connection.execute(
        "SELECT id, hire_id, payload_json FROM source_records WHERE category='equipment' "
        "AND (hire_id=? OR hire_id IS NULL) ORDER BY id",
        (hire["id"],),
    ).fetchall()
    facts: dict = {"profile_location": hire["location_id"], "available_device_record_id": None}
    for record in records:
        payload = json.loads(record["payload_json"])
        if record["hire_id"] == hire["id"]:
            facts["assigned_asset"] = payload["asset_tag"]
            facts["assigned_state"] = payload["state"]
            facts["assigned_device_location"] = payload["location_id"]
        elif payload["state"] == "AVAILABLE" and payload["location_id"] == hire["location_id"]:
            facts["available_device_record_id"] = (
                facts["available_device_record_id"] or record["id"]
            )
    if "assigned_asset" in facts:
        facts["available_device_record_id"] = None
    evidence = [
        item
        for item in check_hire(connection, hire["id"])
        if item.check_type == "device_handover_recorded"
    ]
    return ToolObservation(evidence=evidence, facts=facts)


def _payroll(connection, hire, context):
    evidence = [
        item
        for item in check_hire(connection, hire["id"])
        if item.check_type == "payroll_setup_confirmed"
    ]
    facts = dict(evidence[0].observed) if evidence else {"payroll_record": False}
    return ToolObservation(evidence=evidence, facts=facts)


def _outcomes(connection, hire, context):
    evidence = check_hire(connection, hire["id"])
    facts = {item.check_type: f"{item.result.value} ({item.reason_code})" for item in evidence}
    return ToolObservation(evidence=evidence, facts=facts)


TOOLS = {
    "get_hire_context": _hire_context,
    "get_onboarding_tasks": _tasks,
    "get_document_evidence": _documents,
    "get_applicable_policy": _policy,
    "get_equipment_status": _equipment,
    "get_payroll_setup_status": _payroll,
    "get_task_outcome_evidence": _outcomes,
}


def dispatch_read(tool_name: str, context: InvestigationContext) -> ToolObservation:
    """Re-reads the user's current identity and scope on every call, including after a long wait."""
    with connect() as connection:
        user = load_user(connection, context.user.id)
        if user is None or context.hire_id not in user.hire_ids:
            raise ScopeLost()
        hire = get_hire_row(connection, context.hire_id)
        return TOOLS[tool_name](connection, hire, context)
