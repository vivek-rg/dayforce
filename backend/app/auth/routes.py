import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, Request

from app.auth import service
from app.auth.permissions import require
from app.shared.contracts import (
    AccountCreate,
    LoginRequest,
    PasswordResetCreate,
    PasswordResetList,
    Session,
    TemporaryPassword,
    User,
)
from app.shared.db import connect
from app.shared.errors import fail

router = APIRouter(tags=["auth"])
PUBLIC_LIMIT_PER_HOUR = 30
_public_calls: dict[str, deque[float]] = defaultdict(deque)


def _limit_public_form(request: Request) -> None:
    """A small brake on the two public forms. Per process, which suits one local instance."""
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    calls = _public_calls[client]
    while calls and now - calls[0] > 3600:
        calls.popleft()
    if len(calls) >= PUBLIC_LIMIT_PER_HOUR:
        fail(429, "TOO_MANY_ATTEMPTS", "Too many attempts. Try again later.")
    calls.append(now)


@router.post("/sessions", response_model=Session, summary="Create a local demo bearer session")
def create_session(body: LoginRequest):
    return service.login(body.user_id, body.password)


@router.delete("/sessions/current", status_code=204, summary="Revoke current bearer session")
def delete_session(request: Request, user: User = Depends(service.require_user)):
    service.logout(request)


@router.get("/me", response_model=User, summary="Read authenticated identity and hire scopes")
def me(user: User = Depends(service.require_user)):
    return user


@router.post(
    "/accounts", response_model=Session, status_code=201, summary="Create a new employee account"
)
def create_account(body: AccountCreate, request: Request):
    _limit_public_form(request)
    return service.create_account(body.display_name, body.email, body.password)


@router.post("/password-resets", status_code=202, summary="Ask HR for a password reset")
def request_password_reset(body: PasswordResetCreate, request: Request):
    _limit_public_form(request)
    service.request_password_reset(body.email)


@router.get(
    "/password-resets", response_model=PasswordResetList, summary="List open reset requests"
)
def list_password_resets(user: User = Depends(service.require_user)):
    require(user.role, "password.reset")
    with connect() as connection:
        return PasswordResetList(items=service.open_password_resets(connection))


@router.post(
    "/password-resets/{reset_id}/temporary-password",
    response_model=TemporaryPassword,
    summary="Issue a temporary password, shown once",
)
def issue_temporary_password(reset_id: str, user: User = Depends(service.require_user)):
    require(user.role, "password.reset")
    return service.issue_temporary_password(reset_id, user)
