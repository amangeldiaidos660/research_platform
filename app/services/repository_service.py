from __future__ import annotations

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.db.models import Author, IngestionJob, Publication, PublicationAuthor, PublicationTopic, Topic
from app.services.processor_service import normalize_text


def _apply_publication_filters(
    query,
    *,
    year: int | None,
    topic_id: int | None,
    author_id: int | None,
):
    if year:
        query = query.filter(Publication.publication_year == year)
    if topic_id:
        query = query.join(PublicationTopic).filter(PublicationTopic.topic_id == topic_id)
    if author_id:
        query = query.join(PublicationAuthor).filter(PublicationAuthor.author_id == author_id)
    return query


def _apply_publication_sort(query, *, sort: str):
    if sort == "citations":
        return query.order_by(desc(Publication.cited_by_count))
    return query.order_by(desc(Publication.publication_year), desc(Publication.id))


def list_publications(
    db: Session,
    *,
    q: str | None = None,
    year: int | None = None,
    topic_id: int | None = None,
    author_id: int | None = None,
    sort: str = "recent",
    limit: int = 20,
) -> list[Publication]:
    query = db.query(Publication)
    if q:
        normalized = normalize_text(q) or ""
        query = query.filter(
            or_(
                Publication.normalized_title.contains(normalized),
                Publication.title.ilike(f"%{q}%"),
                Publication.keywords_cache.ilike(f"%{q}%"),
            )
        )
    query = _apply_publication_filters(
        query,
        year=year,
        topic_id=topic_id,
        author_id=author_id,
    )
    query = _apply_publication_sort(query, sort=sort)
    items = query.distinct().limit(limit).all()

    if items or not q:
        return items

    fallback_query = db.query(Publication).filter(Publication.abstract_text.ilike(f"%{q}%"))
    fallback_query = _apply_publication_filters(
        fallback_query,
        year=year,
        topic_id=topic_id,
        author_id=author_id,
    )
    fallback_query = _apply_publication_sort(fallback_query, sort=sort)
    return fallback_query.distinct().limit(limit).all()


def get_publication_detail(db: Session, publication_id: int) -> Publication | None:
    return (
        db.query(Publication)
        .options(
            joinedload(Publication.author_links).joinedload(PublicationAuthor.author),
            joinedload(Publication.topic_links).joinedload(PublicationTopic.topic),
        )
        .filter(Publication.id == publication_id)
        .first()
    )


def list_authors(db: Session, *, q: str | None = None, limit: int = 30) -> list[Author]:
    query = db.query(Author)
    if q:
        query = query.filter(Author.display_name.ilike(f"%{q}%"))
    return query.order_by(desc(Author.cited_by_count), desc(Author.works_count)).limit(limit).all()


def get_author_detail(db: Session, author_id: int) -> Author | None:
    return (
        db.query(Author)
        .options(joinedload(Author.publication_links).joinedload(PublicationAuthor.publication))
        .filter(Author.id == author_id)
        .first()
    )


def list_topics(db: Session, *, q: str | None = None, limit: int = 30) -> list[Topic]:
    query = db.query(Topic)
    if q:
        query = query.filter(Topic.name.ilike(f"%{q}%"))
    return query.order_by(desc(Topic.works_count), desc(Topic.cited_by_count)).limit(limit).all()


def get_topic_detail(db: Session, topic_id: int) -> Topic | None:
    return db.query(Topic).filter(Topic.id == topic_id).first()


def list_ingestion_jobs(db: Session, limit: int = 20) -> list[IngestionJob]:
    return db.query(IngestionJob).order_by(desc(IngestionJob.id)).limit(limit).all()


def dashboard_counts(db: Session) -> dict[str, int]:
    return {
        "publications_total": db.query(func.count(Publication.id)).scalar() or 0,
        "authors_total": db.query(func.count(Author.id)).scalar() or 0,
        "topics_total": db.query(func.count(Topic.id)).scalar() or 0,
        "citations_total": db.query(func.coalesce(func.sum(Publication.cited_by_count), 0)).scalar() or 0,
    }
