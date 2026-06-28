from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.security.dependencies import get_current_user
from app.security.jwt import create_access_token
from app.services.audit_log_service import create_audit_log
from app.services.user_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Autentica al usuario y devuelve un JWT.
    """
    user = authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
    )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    if not user:
        create_audit_log(
            db=db,
            action="LOGIN_FAILED",
            user_id=None,
            ip_address=client_ip,
            user_agent=user_agent,
            detail=f"Failed login attempt for email={payload.email}",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    create_audit_log(
        db=db,
        action="LOGIN_SUCCESS",
        user_id=user.id,
        ip_address=client_ip,
        user_agent=user_agent,
        detail="User authenticated successfully",
    )

    access_token = create_access_token(
        subject=str(user.id),
        email=user.email,
        role=user.role,
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Devuelve información del usuario autenticado.
    """
    return current_user
