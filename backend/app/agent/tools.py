"""Track 6/P04: server-bound hire/case scope, no IDs or URLs chosen by the model."""

from app.shared.contracts import InvestigationContext, ToolObservation


def dispatch_read(tool_name: str, context: InvestigationContext) -> ToolObservation:
    # TODO P04: exact ReadStep allowlist, current auth/field filtering, sanitized evidence IDs.
    raise NotImplementedError("P04: dispatch_read")
