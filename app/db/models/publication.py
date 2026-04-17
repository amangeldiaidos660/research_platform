from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class Publication(TimestampMixin, Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True)
    openalex_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(1000))
    normalized_title: Mapped[str | None] = mapped_column(String(1000), index=True, nullable=True)
    abstract_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    abstract_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_date: Mapped[str | None] = mapped_column(String(25), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    doi: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    primary_location_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    open_access_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    keywords_cache: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    favorites = relationship("FavoritePublication", back_populates="publication", cascade="all,delete")
    collection_items = relationship("CollectionItem", back_populates="publication", cascade="all,delete")
    author_links = relationship(
        "PublicationAuthor",
        back_populates="publication",
        cascade="all,delete-orphan",
    )
    topic_links = relationship(
        "PublicationTopic",
        back_populates="publication",
        cascade="all,delete-orphan",
    )
