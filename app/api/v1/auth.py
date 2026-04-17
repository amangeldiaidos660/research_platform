from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import Token, UserLogin, UserRegister
from app.services.auth_service import authenticate_user, register_user

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    db: Session = Depends(get_db),
) -> Token:
    return register_user(db, payload)


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    return authenticate_user(db, payload)


@router.post("/token", response_model=Token, include_in_schema=False)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    return authenticate_user(
        db,
        UserLogin(email=form_data.username, password=form_data.password),
    )
