"""Track 1/P02 owns sessions, hash verification and object/field authorization."""

from app.shared.contracts import User


def require_user() -> User:
    # TODO P02: FastAPI dependency using Authorization: Bearer; 401 on absent/invalid token.
    raise NotImplementedError("P02: require_user")


def require_hire_scope(user: User, hire_id: str) -> None:
    # TODO P02: active identity + persisted scope; deny before any record/model read.
    raise NotImplementedError("P02: require_hire_scope")
