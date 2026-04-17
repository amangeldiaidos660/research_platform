from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OpenAlexListQuery(BaseModel):
    search: str | None = None
    filter: str | None = None
    select: str | None = None
    sort: str | None = None
    per_page: int = Field(default=25, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    cursor: str | None = None
    sample: int | None = Field(default=None, ge=1)


class IngestRequest(BaseModel):
    search: str | None = None
    filter: str | None = None
    per_page: int = Field(default=25, ge=1, le=100)
    pages: int = Field(default=1, ge=1, le=20)
    cursor: bool = False
    select: str | None = None


class IngestionJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    entity_type: str
    status: str
    query_text: str | None
    page_count: int
    processed_count: int
    inserted_count: int
    updated_count: int
    error_message: str | None
