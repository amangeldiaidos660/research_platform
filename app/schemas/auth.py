from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    full_name: str | None
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

