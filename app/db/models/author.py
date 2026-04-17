from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class Author(TimestampMixin, Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    openalex_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), index=True)
    orcid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    works_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    cited_by_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    summary_stats_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_known_institution: Mapped[str | None] = mapped_column(String(255), nullable=True)

    publication_links = relationship(
        "PublicationAuthor",
        back_populates="author",
        cascade="all,delete-orphan",
    )

