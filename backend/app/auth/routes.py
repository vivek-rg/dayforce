from fastapi import APIRouter

from app.shared.contracts import LoginRequest, Session, User
from app.shared.errors import not_implemented

router = APIRouter(tags=["auth"])


@router.post("/sessions", response_model=Session, summary="Create a local demo bearer session")
def create_session(body: LoginRequest):
    # TODO P02: verify active seeded user/password hash; issue hashed expiring token.
    not_implemented()


@router.delete("/sessions/current", status_code=204, summary="Revoke current bearer session")
def delete_session():
    # TODO P02: authenticate and remove the hashed token. No browser role claims.
    not_implemented()


@router.get("/me", response_model=User, summary="Read authenticated identity and hire scopes")
def me():
    # TODO P02: return only authenticated current identity from server storage.
    not_implemented()
