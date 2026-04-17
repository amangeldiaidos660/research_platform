from __future__ import annotations

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.models import Author, Publication, PublicationAuthor, PublicationTopic, Topic
from app.schemas.analytics import AnalyticsPoint, DashboardAnalytics, TopicGrowthPoint
from app.services.repository_service import dashboard_counts


def get_top_publications(db: Session, limit: int = 10, topic_id: int | None = None) -> list[AnalyticsPoint]:
    query = db.query(Publication.title, Publication.cited_by_count)
    if topic_id:
        query = query.join(PublicationTopic).filter(PublicationTopic.topic_id == topic_id)
    rows = query.order_by(desc(Publication.cited_by_count)).limit(limit).all()
    return [AnalyticsPoint(label=title, value=value or 0) for title, value in rows]


def get_top_authors(db: Session, limit: int = 10, topic_id: int | None = None) -> list[AnalyticsPoint]:
    query = db.query(Author.display_name, func.count(PublicationAuthor.id).label("works"))
    query = query.join(PublicationAuthor, PublicationAuthor.author_id == Author.id)
    if topic_id:
        query = query.join(Publication, Publication.id == PublicationAuthor.publication_id)
        query = query.join(PublicationTopic, PublicationTopic.publication_id == Publication.id)
        query = query.filter(PublicationTopic.topic_id == topic_id)

    rows = (
        query.group_by(Author.id, Author.display_name)
        .order_by(desc(func.count(PublicationAuthor.id)), desc(Author.cited_by_count))
        .limit(limit)
        .all()
    )
    return [AnalyticsPoint(label=name, value=value) for name, value in rows]


def get_publication_trends(db: Session, limit: int = 20) -> list[AnalyticsPoint]:
    rows = (
        db.query(Publication.publication_year, func.count(Publication.id))
        .filter(Publication.publication_year.isnot(None))
        .group_by(Publication.publication_year)
        .order_by(Publication.publication_year)
        .limit(limit)
        .all()
    )
    return [AnalyticsPoint(label=str(year), value=count) for year, count in rows]


def get_publication_distribution_by_topic(db: Session, limit: int = 12) -> list[AnalyticsPoint]:
    rows = (
        db.query(Topic.name, func.count(PublicationTopic.id))
        .join(PublicationTopic, PublicationTopic.topic_id == Topic.id)
        .group_by(Topic.id, Topic.name)
        .order_by(desc(func.count(PublicationTopic.id)))
        .limit(limit)
        .all()
    )
    return [AnalyticsPoint(label=name, value=count) for name, count in rows]


def get_topic_growth(db: Session, topic_id: int) -> list[TopicGrowthPoint]:
    rows = (
        db.query(Topic.name, Publication.publication_year, func.count(Publication.id))
        .join(PublicationTopic, PublicationTopic.topic_id == Topic.id)
        .join(Publication, Publication.id == PublicationTopic.publication_id)
        .filter(Topic.id == topic_id, Publication.publication_year.isnot(None))
        .group_by(Topic.name, Publication.publication_year)
        .order_by(Publication.publication_year)
        .all()
    )
    return [TopicGrowthPoint(topic=topic, year=year, works_count=count) for topic, year, count in rows]


def get_dashboard_analytics(db: Session) -> DashboardAnalytics:
    counts = dashboard_counts(db)
    return DashboardAnalytics(
        **counts,
        top_publications=get_top_publications(db),
        top_authors=get_top_authors(db),
        publications_by_year=get_publication_trends(db),
        publications_by_topic=get_publication_distribution_by_topic(db),
    )
