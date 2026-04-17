from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import AnalyticsPoint, DashboardAnalytics, TopicGrowthPoint
from app.services.analytics_service import (
    get_dashboard_analytics,
    get_publication_distribution_by_topic,
    get_publication_trends,
    get_top_authors,
    get_top_publications,
    get_topic_growth,
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardAnalytics, summary="Dashboard analytics")
async def read_dashboard_analytics(db: Session = Depends(get_db)) -> DashboardAnalytics:
    return get_dashboard_analytics(db)


@router.get("/top-publications", response_model=list[AnalyticsPoint], summary="Top publications")
async def read_top_publications(
    limit: int = Query(default=10, ge=1, le=50),
    topic_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[AnalyticsPoint]:
    return get_top_publications(db, limit=limit, topic_id=topic_id)


@router.get("/top-authors", response_model=list[AnalyticsPoint], summary="Top authors")
async def read_top_authors(
    limit: int = Query(default=10, ge=1, le=50),
    topic_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[AnalyticsPoint]:
    return get_top_authors(db, limit=limit, topic_id=topic_id)


@router.get("/trends", response_model=list[AnalyticsPoint], summary="Publication trends by year")
async def read_publication_trends(db: Session = Depends(get_db)) -> list[AnalyticsPoint]:
    return get_publication_trends(db)


@router.get("/distribution/topics", response_model=list[AnalyticsPoint], summary="Topic distribution")
async def read_topic_distribution(db: Session = Depends(get_db)) -> list[AnalyticsPoint]:
    return get_publication_distribution_by_topic(db)


@router.get("/topic-growth/{topic_id}", response_model=list[TopicGrowthPoint], summary="Topic growth")
async def read_topic_growth(
    topic_id: int,
    db: Session = Depends(get_db),
) -> list[TopicGrowthPoint]:
    return get_topic_growth(db, topic_id=topic_id)
