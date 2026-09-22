from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegistrationRequest


class AuthService:
    def register(self, session: Session, payload: RegistrationRequest) -> User:
        user = User(email=payload.email.lower(), hashed_password=hash_password(payload.password))
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError("An account with this email already exists.")
        session.refresh(user)
        return user

    def authenticate(self, session: Session, payload: LoginRequest) -> User | None:
        user = session.scalar(select(User).where(User.email == payload.email.lower()))
        if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
            return None
        return user

    def get_user(self, session: Session, user_id: str) -> User | None:
        return session.get(User, user_id)
