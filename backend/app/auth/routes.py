from fastapi import APIRouter, Depends, Request

from app.auth import service
from app.shared.contracts import LoginRequest, Session, User

router = APIRouter(tags=["auth"])


@router.post("/sessions", response_model=Session, summary="Create a local demo bearer session")
def create_session(body: LoginRequest):
    return service.login(body.user_id, body.password)


@router.delete("/sessions/current", status_code=204, summary="Revoke current bearer session")
def delete_session(request: Request, user: User = Depends(service.require_user)):
    service.logout(request)


@router.get("/me", response_model=User, summary="Read authenticated identity and hire scopes")
def me(user: User = Depends(service.require_user)):
    return user
