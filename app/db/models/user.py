from __future__ import annotations

from sqlalchemy import Boolean, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    favorites = relationship("FavoritePublication", back_populates="user", cascade="all,delete")
    saved_searches = relationship("SavedSearch", back_populates="user", cascade="all,delete")
    collections = relationship("Collection", back_populates="user", cascade="all,delete")
    topic_subscriptions = relationship(
        "TopicSubscription",
        back_populates="user",
        cascade="all,delete",
    )
