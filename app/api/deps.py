from __future__ import annotations

from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.models import User
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def _username_from_email(email: str) -> str:
    base = email.split("@", 1)[0].lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in base).strip("_")
    return (cleaned or "user")[:40]


def _get_or_create_supabase_user(db: Session, payload: dict) -> User | None:
    issuer = str(payload.get("iss") or "").rstrip("/")
    expected_issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1"
    email = payload.get("email")
    expires_at = payload.get("exp")
    if not settings.supabase_url or issuer != expected_issuer or not email:
        return None
    if expires_at and datetime.now(UTC).timestamp() > float(expires_at):
        return None

    user = db.query(User).filter(User.email == email.lower()).first()
    if user:
        return user

    metadata = payload.get("user_metadata") or {}
    username_base = _username_from_email(email)
    username = username_base
    suffix = 1
    while db.query(User).filter(User.username == username).first():
        suffix += 1
        username = f"{username_base[:35]}_{suffix}"

    user = User(
        email=email.lower(),
        username=username,
        full_name=metadata.get("full_name") or metadata.get("name"),
        hashed_password="supabase-oauth",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if not payload:
        try:
            payload = jwt.get_unverified_claims(token)
        except JWTError:
            payload = None

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        user = _get_or_create_supabase_user(db, payload)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
