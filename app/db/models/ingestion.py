from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class IngestionJob(TimestampMixin, Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50), default="openalex")
    entity_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    query_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    filters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    processed_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    inserted_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    updated_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
