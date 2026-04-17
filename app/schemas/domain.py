from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openalex_id: str
    display_name: str
    orcid: str | None
    works_count: int
    cited_by_count: int
    last_known_institution: str | None


class TopicSlimRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openalex_id: str
    name: str
    works_count: int
    cited_by_count: int
    domain_name: str | None
    field_name: str | None
    subfield_name: str | None


class PublicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openalex_id: str
    title: str
    normalized_title: str | None
    abstract_summary: str | None
    publication_year: int | None
    cited_by_count: int
    doi: str | None
    type: str | None
    language: str | None
    primary_location_source: str | None


class PublicationDetailRead(PublicationRead):
    abstract_text: str | None
    publication_date: str | None
    open_access_url: str | None
    keywords_cache: str | None
    authors: list[AuthorRead] = Field(default_factory=list)
    topics: list[TopicSlimRead] = Field(default_factory=list)


class TopicDetailRead(TopicSlimRead):
    description: str | None
    keywords_cache: str | None


class AuthorDetailRead(AuthorRead):
    summary_stats_json: str | None
    publications: list[PublicationRead] = Field(default_factory=list)
