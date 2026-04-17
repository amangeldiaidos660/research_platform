from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PublicationRefCreate(BaseModel):
    openalex_id: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=1000)
    publication_year: int | None = None
    cited_by_count: int = 0
    doi: str | None = None
    primary_location_source: str | None = None


class PublicationRefRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openalex_id: str
    title: str
    publication_year: int | None
    cited_by_count: int
    doi: str | None
    primary_location_source: str | None


class FavoriteCreate(BaseModel):
    publication: PublicationRefCreate


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publication: PublicationRefRead


class SavedSearchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    query: str = Field(min_length=1, max_length=500)
    filters_json: dict = Field(default_factory=dict)


class SavedSearchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    query: str
    filters_json: dict


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class CollectionItemCreate(BaseModel):
    publication: PublicationRefCreate


class CollectionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publication: PublicationRefRead


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    items: list[CollectionItemRead] = Field(default_factory=list)


class TopicCreate(BaseModel):
    openalex_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    works_count: int = 0
    keywords_cache: str | None = None


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openalex_id: str
    name: str
    description: str | None
    works_count: int
    keywords_cache: str | None


class TopicSubscriptionCreate(BaseModel):
    topic: TopicCreate


class TopicSubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: TopicRead
