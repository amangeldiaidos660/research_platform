from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models import User
from app.schemas.auth import Token, UserLogin, UserRead, UserRegister


def register_user(db: Session, payload: UserRegister) -> Token:
    email = payload.email.lower()
    username = payload.username.lower()

    existing_user = (
        db.query(User)
        .filter((User.email == email) | (User.username == username))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists",
        )

    user = User(
        email=email,
        username=username,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.email)
    return Token(access_token=token, user=UserRead.model_validate(user))


def authenticate_user(db: Session, payload: UserLogin) -> Token:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(subject=user.email)
    return Token(access_token=token, user=UserRead.model_validate(user))

