"""Track 5/P05 owns approval gate, conditional local mutations and read-back."""

from sqlite3 import Connection

from app.shared.contracts import ActionPayload, ActionResult, InvestigationContext, Proposal


def save_proposal(
    connection: Connection,
    context: InvestigationContext,
    payload: ActionPayload,
    evidence_ids: list[str],
) -> Proposal:
    # TODO P05: validate two allowed actions; server derives authority/versions, never model.
    raise NotImplementedError("P05: save_proposal")


def execute_approved_action(action_id: str) -> ActionResult:
    # TODO P05: transactional decision/version checks, unique action effect, fresh read-back.
    raise NotImplementedError("P05: execute_approved_action")
