from typing import NoReturn

from fastapi import HTTPException


def fail(status: int, code: str, message: str) -> NoReturn:
    """Raise the one sanitized error envelope used by every route."""
    raise HTTPException(
        status_code=status, detail={"code": code, "message": message, "details": []}
    )


def not_found() -> NoReturn:
    # Same response for unknown and out-of-scope records, so scope cannot be probed.
    fail(404, "NOT_FOUND", "Record not found.")


def forbidden() -> NoReturn:
    fail(403, "FORBIDDEN", "Your role cannot perform this operation.")


def stale() -> NoReturn:
    fail(409, "STALE_VERSION", "This record changed. Reload and try again.")


def invalid_state(message: str) -> NoReturn:
    fail(409, "INVALID_STATE", message)


def not_implemented() -> NoReturn:
    fail(501, "FEATURE_NOT_IMPLEMENTED", "Contract reserved. Feature phase is not implemented.")
