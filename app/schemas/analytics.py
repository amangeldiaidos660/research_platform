from __future__ import annotations

from pydantic import BaseModel


class AnalyticsPoint(BaseModel):
    label: str
    value: int | float


class TopicGrowthPoint(BaseModel):
    topic: str
    year: int
    works_count: int


class DashboardAnalytics(BaseModel):
    publications_total: int
    authors_total: int
    topics_total: int
    citations_total: int
    top_publications: list[AnalyticsPoint]
    top_authors: list[AnalyticsPoint]
    publications_by_year: list[AnalyticsPoint]
    publications_by_topic: list[AnalyticsPoint]
