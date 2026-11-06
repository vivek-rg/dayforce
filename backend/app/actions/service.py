"""The approval gate. Immutable proposal, right reviewer, expiry, conditional write, read-back."""

import json
import sqlite3
from datetime import UTC, datetime, timedelta

from app.evidence.service import check_hire, latest_evidence
from app.notifications.service import notify, notify_role
from app.planning.service import (
    apply_location_change,
    get_hire_row,
    preview_location_change,
    refresh_completion,
)
from app.shared.contracts import (
    ActionPayload,
    ActionResult,
    DecisionResult,
    ExpectedVersions,
    InvestigationContext,
    PlanDiff,
    Proposal,
    Role,
    User,
)
from app.shared.db import connect
from app.shared.errors import fail, forbidden, invalid_state, not_found, stale
from app.shared.util import audit, new_id, now_iso

PROPOSAL_HOURS = 72
FAILURE_TEXT = {
    "DEVICE_NO_LONGER_AVAILABLE": "Not done: that device is no longer available.",
    "STALE_INPUTS": "Not done: the records changed after approval. Request a new proposal.",
    "NO_APPROVAL": "Not done: no approval is on record.",
}
RESERVER_REVIEWER = {"CHANGE_WORK_LOCATION": "HR", "RESERVE_EQUIPMENT": "IT"}


def _active_or_manual_case(connection, hire_id: str, user: User) -> str:
    row = connection.execute(
        "SELECT id FROM cases WHERE hire_id=? AND state NOT IN ('RESOLVED','ESCALATED')",
        (hire_id,),
    ).fetchone()
    if row:
        return row["id"]
    case_id = new_id("CASE")
    connection.execute(
        "INSERT INTO cases (id, hire_id, opened_by, message, state, kind, thread_id, created_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            case_id,
            hire_id,
            user.id,
            "Manual request",
            "WAITING_APPROVAL",
            "MANUAL",
            new_id("THREAD"),
            now_iso(),
        ),
    )
    return case_id


def save_proposal(
    connection: sqlite3.Connection,
    context: InvestigationContext,
    payload: ActionPayload,
    evidence_ids: list[str],
) -> Proposal:
    """The server derives reviewer, versions and expiry. The caller can only name the action."""
    hire = get_hire_row(connection, context.hire_id)
    for evidence_id in evidence_ids:
        row = connection.execute(
            "SELECT hire_id FROM evidence WHERE id=?", (evidence_id,)
        ).fetchone()
        if row is None or row["hire_id"] != context.hire_id:
            fail(422, "VALIDATION_ERROR", "Cited evidence does not belong to this hire.")
    if connection.execute(
        "SELECT 1 FROM proposals p LEFT JOIN decisions d ON d.proposal_id=p.id "
        "WHERE p.case_id=? AND d.proposal_id IS NULL AND p.payload_json=? AND p.expires_at>?",
        (context.case_id, payload.model_dump_json(), now_iso()),
    ).fetchone():
        invalid_state("An identical proposal is already awaiting review.")
    policy = connection.execute(
        "SELECT policy_id, policy_version FROM tasks WHERE hire_id=? LIMIT 1", (hire["id"],)
    ).fetchone()
    source_id = source_version = None
    diff: PlanDiff | None = None
    if payload.action_type == "CHANGE_WORK_LOCATION":
        if payload.location_id == hire["location_id"]:
            invalid_state("The profile already has this location.")
        diff = preview_location_change(connection, hire["id"], payload.location_id)
    else:
        record = connection.execute(
            "SELECT * FROM source_records WHERE id=? AND category='equipment'",
            (payload.equipment_record_id,),
        ).fetchone()
        if record is None:
            not_found()
        device = json.loads(record["payload_json"])
        if device["state"] != "AVAILABLE" or record["hire_id"] is not None:
            invalid_state("That device is not available.")
        if device["location_id"] != hire["location_id"]:
            invalid_state("That device is not at the hire's approved location.")
        source_id, source_version = record["id"], record["version"]
    expected = ExpectedVersions(
        profile_version=hire["profile_version"],
        plan_version=hire["plan_version"],
        policy_id=policy["policy_id"],
        policy_version=policy["policy_version"],
        source_record_id=source_id,
        source_version=source_version,
    )
    proposal_id = new_id("PROP")
    reviewer = RESERVER_REVIEWER[payload.action_type]
    expires = datetime.now(UTC) + timedelta(hours=PROPOSAL_HOURS)
    connection.execute(
        "INSERT INTO proposals (id, case_id, action_type, payload_json, evidence_ids_json, "
        "expected_versions_json, plan_diff_json, reviewer_role, expires_at, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            proposal_id,
            context.case_id,
            payload.action_type,
            payload.model_dump_json(),
            json.dumps(evidence_ids),
            expected.model_dump_json(),
            diff.model_dump_json() if diff else None,
            reviewer,
            expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
            now_iso(),
        ),
    )
    audit(
        connection,
        hire["id"],
        "PROPOSAL_CREATED",
        f"{payload.action_type} proposed, awaiting {reviewer} review.",
        context.user.id,
        context.case_id,
    )
    notify_role(
        connection,
        reviewer,
        hire["id"],
        kind="APPROVAL_REQUEST",
        title="Approval needed",
        body=f"{payload.action_type.replace('_', ' ').title()} for {hire['display_name']}",
        dedupe_key=f"proposal:{proposal_id}",
    )
    return get_proposal(connection, proposal_id)


def get_proposal(connection: sqlite3.Connection, proposal_id: str) -> Proposal:
    row = connection.execute(
        "SELECT p.*, c.hire_id, h.display_name AS hire_name, d.decision, a.state AS action_state, "
        "a.observed_json FROM proposals p JOIN cases c ON c.id=p.case_id "
        "JOIN hires h ON h.id=c.hire_id LEFT JOIN decisions d ON d.proposal_id=p.id "
        "LEFT JOIN actions a ON a.proposal_id=p.id WHERE p.id=?",
        (proposal_id,),
    ).fetchone()
    if row is None:
        not_found()
    observed = json.loads(row["observed_json"]) if row["observed_json"] else {}
    return Proposal(
        id=row["id"],
        case_id=row["case_id"],
        hire_id=row["hire_id"],
        hire_name=row["hire_name"],
        payload=json.loads(row["payload_json"]),
        evidence_ids=json.loads(row["evidence_ids_json"]),
        expected_versions=json.loads(row["expected_versions_json"]),
        reviewer_role=row["reviewer_role"],
        expires_at=row["expires_at"],
        plan_diff=json.loads(row["plan_diff_json"]) if row["plan_diff_json"] else None,
        decision=row["decision"],
        action_state=row["action_state"],
        outcome=observed.get("outcome")
        or FAILURE_TEXT.get(observed.get("reason"), observed.get("reason")),
    )


def review_inbox(connection: sqlite3.Connection, user: User) -> list[Proposal]:
    if user.role not in (Role.HR, Role.IT):
        forbidden()
    rows = connection.execute(
        "SELECT p.id, c.hire_id FROM proposals p JOIN cases c ON c.id=p.case_id "
        "WHERE p.reviewer_role=? ORDER BY p.created_at DESC",
        (user.role.value,),
    ).fetchall()
    return [get_proposal(connection, row["id"]) for row in rows if row["hire_id"] in user.hire_ids]


def _versions_current(connection, proposal: Proposal) -> bool:
    hire = get_hire_row(connection, proposal.hire_id)
    expected = proposal.expected_versions
    if (
        hire["profile_version"] != expected.profile_version
        or hire["plan_version"] != expected.plan_version
    ):
        return False
    if expected.source_record_id:
        source = connection.execute(
            "SELECT version FROM source_records WHERE id=?", (expected.source_record_id,)
        ).fetchone()
        return source is not None and source["version"] == expected.source_version
    return True


def decide(
    connection: sqlite3.Connection, proposal_id: str, user: User, decision: str, note: str
) -> DecisionResult:
    proposal = get_proposal(connection, proposal_id)
    if proposal.hire_id not in user.hire_ids:
        not_found()
    if user.role.value != proposal.reviewer_role:
        forbidden()
    existing = connection.execute(
        "SELECT d.decision, a.id AS action_id FROM decisions d "
        "LEFT JOIN actions a ON a.proposal_id=d.proposal_id WHERE d.proposal_id=?",
        (proposal_id,),
    ).fetchone()
    if existing:
        if existing["decision"] != decision:
            fail(409, "INVALID_STATE", "A different decision is already recorded.")
        work = connection.execute(
            "SELECT id FROM work_items WHERE action_id=?", (existing["action_id"],)
        ).fetchone()
        return DecisionResult(
            proposal_id=proposal_id,
            decision=decision,
            action_id=existing["action_id"],
            work_item_id=work["id"] if work else None,
        )
    if decision == "APPROVE":
        if proposal.expires_at.strftime("%Y-%m-%dT%H:%M:%SZ") <= now_iso():
            fail(409, "STALE_VERSION", "This proposal has expired. Request a new one.")
        if not _versions_current(connection, proposal):
            stale()
    connection.execute(
        "INSERT INTO decisions (proposal_id, reviewer_user_id, decision, note, created_at) "
        "VALUES (?,?,?,?,?)",
        (proposal_id, user.id, decision, note, now_iso()),
    )
    audit(
        connection,
        proposal.hire_id,
        f"PROPOSAL_{decision}D" if decision == "APPROVE" else "PROPOSAL_REJECTED",
        f"{proposal.payload.action_type} {decision.lower()} by {user.display_name}.",
        user.id,
        proposal.case_id,
    )
    if decision == "REJECT":
        _after_case_action(connection, proposal.case_id, f"reject:{proposal_id}")
        return DecisionResult(proposal_id=proposal_id, decision="REJECT")
    action_id = new_id("ACT")
    work_id = new_id("WRK")
    connection.execute(
        "INSERT INTO actions (id, proposal_id, state, observed_json, updated_at) "
        "VALUES (?,?,'PENDING','{}',?)",
        (action_id, proposal_id, now_iso()),
    )
    connection.execute(
        "INSERT INTO work_items (id, event_id, case_id, kind, state, action_id, updated_at) "
        "VALUES (?,?,?,'EXECUTE','PENDING',?,?)",
        (work_id, f"execute:{action_id}", proposal.case_id, action_id, now_iso()),
    )
    connection.execute(
        "UPDATE cases SET state='EXECUTING', version=version+1 WHERE id=?", (proposal.case_id,)
    )
    return DecisionResult(
        proposal_id=proposal_id, decision="APPROVE", action_id=action_id, work_item_id=work_id
    )


def _after_case_action(connection, case_id: str, event_key: str) -> None:
    """A manual request finishes here. An investigation resumes with fresh facts."""
    case = connection.execute("SELECT kind, hire_id FROM cases WHERE id=?", (case_id,)).fetchone()
    if case["kind"] == "MANUAL":
        undecided = connection.execute(
            "SELECT 1 FROM proposals p LEFT JOIN decisions d ON d.proposal_id=p.id "
            "WHERE p.case_id=? AND d.proposal_id IS NULL LIMIT 1",
            (case_id,),
        ).fetchone()
        connection.execute(
            "UPDATE cases SET state=?, version=version+1 WHERE id=?",
            ("WAITING_APPROVAL" if undecided else "RESOLVED", case_id),
        )
        return
    connection.execute(
        "UPDATE cases SET state='INVESTIGATING', version=version+1 WHERE id=?", (case_id,)
    )
    connection.execute(
        "INSERT OR IGNORE INTO work_items (id, event_id, case_id, kind, state, updated_at) "
        "VALUES (?,?,?,'RESUME','PENDING',?)",
        (new_id("WRK"), f"resume:{event_key}", case_id, now_iso()),
    )


def execute_approved_action(action_id: str) -> ActionResult:
    """Revalidate, write conditionally in one transaction, then report what is actually stored."""
    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        action = connection.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
        if action is None:
            not_found()
        if action["state"] in ("SUCCEEDED", "FAILED"):
            return _action_result(connection, action_id)
        proposal = get_proposal(connection, action["proposal_id"])
        decision = connection.execute(
            "SELECT reviewer_user_id, decision FROM decisions WHERE proposal_id=?",
            (proposal.id,),
        ).fetchone()
        connection.execute(
            "UPDATE actions SET state='RUNNING', attempts=attempts+1, updated_at=? WHERE id=?",
            (now_iso(), action_id),
        )
        observed: dict = {}
        state = "SUCCEEDED"
        if decision is None or decision["decision"] != "APPROVE":
            state, observed = "FAILED", {"reason": "NO_APPROVAL"}
        elif not _versions_current(connection, proposal):
            state, observed = "FAILED", {"reason": "STALE_INPUTS"}
        else:
            observed = _apply(connection, proposal, decision["reviewer_user_id"], action_id)
            if observed.get("reason"):
                state = "FAILED"
        connection.execute(
            "UPDATE actions SET state=?, observed_json=?, updated_at=? WHERE id=?",
            (state, json.dumps(observed), now_iso(), action_id),
        )
        audit(
            connection,
            proposal.hire_id,
            "ACTION_" + state,
            observed.get("outcome") or observed.get("reason", "Action finished."),
            decision["reviewer_user_id"] if decision else None,
            proposal.case_id,
            action_id,
            event_id=f"action-result:{action_id}",
        )
        check_hire(connection, proposal.hire_id)
        refresh_completion(connection, proposal.hire_id)
        _after_case_action(connection, proposal.case_id, f"executed:{action_id}")
        return _action_result(connection, action_id)


def _apply(connection, proposal: Proposal, actor: str, action_id: str) -> dict:
    hire = get_hire_row(connection, proposal.hire_id)
    if proposal.payload.action_type == "CHANGE_WORK_LOCATION":
        apply_location_change(connection, hire["id"], proposal.payload.location_id, actor)
        fresh = get_hire_row(connection, hire["id"])
        return {
            "location_id": fresh["location_id"],
            "profile_version": fresh["profile_version"],
            "outcome": f"Work location is now {fresh['location_id']}. History was kept.",
        }
    record = connection.execute(
        "SELECT * FROM source_records WHERE id=?", (proposal.payload.equipment_record_id,)
    ).fetchone()
    device = json.loads(record["payload_json"])
    if device["state"] != "AVAILABLE" or record["hire_id"] is not None:
        return {"reason": "DEVICE_NO_LONGER_AVAILABLE"}
    device.update(state="RESERVED", assignee_hire_id=hire["id"])
    cursor = connection.execute(
        "UPDATE source_records SET payload_json=?, hire_id=?, version=version+1, observed_at=?, "
        "updated_by=? WHERE id=? AND version=? AND hire_id IS NULL",
        (
            json.dumps(device),
            hire["id"],
            now_iso(),
            actor,
            record["id"],
            proposal.expected_versions.source_version,
        ),
    )
    if cursor.rowcount != 1:
        return {"reason": "DEVICE_NO_LONGER_AVAILABLE"}
    # Read back from storage. The outcome text comes from the stored state, not from the intent.
    stored = json.loads(
        connection.execute(
            "SELECT payload_json FROM source_records WHERE id=?", (record["id"],)
        ).fetchone()["payload_json"]
    )
    if hire["employee_user_id"]:
        notify(
            connection,
            hire["employee_user_id"],
            "EQUIPMENT_ALLOCATED",
            "Equipment reserved for you",
            f"{stored['asset_tag']} is reserved. Collection is still pending.",
            f"reserved:{action_id}",
            hire_id=hire["id"],
        )
    return {
        "asset_tag": stored["asset_tag"],
        "state": stored["state"],
        "assignee_hire_id": stored["assignee_hire_id"],
        "outcome": f"{stored['asset_tag']} reserved; collection pending.",
    }


def _action_result(connection, action_id: str) -> ActionResult:
    action = connection.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
    proposal = get_proposal(connection, action["proposal_id"])
    return ActionResult(
        action_id=action_id,
        state=action["state"],
        observed=json.loads(action["observed_json"]),
        evidence=latest_evidence(connection, proposal.hire_id),
    )
