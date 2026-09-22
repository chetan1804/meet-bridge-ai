from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.auth import LoginRequest, RegistrationRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["authentication"])
service = AuthService()
bearer_scheme = HTTPBearer(auto_error=False)
DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_current_user(
    session: DatabaseSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    user = service.get_user(session, payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegistrationRequest, session: DatabaseSession) -> TokenResponse:
    try:
        user = service.register(session, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: DatabaseSession) -> TokenResponse:
    user = service.authenticate(session, payload)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
