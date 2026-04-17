from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.db.models import (
    Author,
    IngestionJob,
    Publication,
    PublicationAuthor,
    PublicationTopic,
    Topic,
)
from app.services.openalex_client import OpenAlexClient
from app.services.processor_service import extract_keywords, normalize_text, reconstruct_abstract, summarize_text


WORKS_SELECT = ",".join(
    [
        "id",
        "doi",
        "display_name",
        "publication_year",
        "publication_date",
        "cited_by_count",
        "type",
        "language",
        "abstract_inverted_index",
        "open_access",
        "primary_location",
        "authorships",
        "topics",
    ]
)

AUTHORS_SELECT = "id,display_name,orcid,works_count,cited_by_count,summary_stats,last_known_institutions"
TOPICS_SELECT = "id,display_name,description,works_count,cited_by_count,keywords,subfield,field,domain"


def start_ingestion_job(
    db: Session,
    *,
    entity_type: str,
    query_text: str | None,
    filters_json: dict | None,
) -> IngestionJob:
    job = IngestionJob(
        source="openalex",
        entity_type=entity_type,
        status="running",
        query_text=query_text,
        filters_json=json.dumps(filters_json or {}, ensure_ascii=False),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def finish_job(
    db: Session,
    job: IngestionJob,
    *,
    status: str,
    page_count: int,
    processed_count: int,
    inserted_count: int,
    updated_count: int,
    error_message: str | None = None,
) -> IngestionJob:
    job.status = status
    job.page_count = page_count
    job.processed_count = processed_count
    job.inserted_count = inserted_count
    job.updated_count = updated_count
    job.error_message = error_message
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def upsert_author(db: Session, payload: dict) -> tuple[Author, bool]:
    openalex_id = payload["id"]
    author = db.query(Author).filter(Author.openalex_id == openalex_id).first()
    created = author is None
    if author is None:
        author = Author(openalex_id=openalex_id, display_name=payload.get("display_name") or "Unknown")
        db.add(author)

    last_known = payload.get("last_known_institutions") or []
    institution_name = last_known[0].get("display_name") if last_known else None
    author.display_name = payload.get("display_name") or author.display_name
    author.orcid = payload.get("orcid")
    author.works_count = payload.get("works_count") or 0
    author.cited_by_count = payload.get("cited_by_count") or 0
    author.last_known_institution = institution_name
    author.summary_stats_json = json.dumps(payload.get("summary_stats") or {}, ensure_ascii=False)
    db.flush()
    return author, created


def upsert_topic(db: Session, payload: dict) -> tuple[Topic, bool]:
    openalex_id = payload["id"]
    topic = db.query(Topic).filter(Topic.openalex_id == openalex_id).first()
    created = topic is None
    if topic is None:
        topic = Topic(openalex_id=openalex_id, name=payload.get("display_name") or "Unknown topic")
        db.add(topic)

    keywords = payload.get("keywords") or []
    topic.name = payload.get("display_name") or topic.name
    topic.description = payload.get("description")
    topic.works_count = payload.get("works_count") or 0
    topic.cited_by_count = payload.get("cited_by_count") or 0
    topic.domain_name = (payload.get("domain") or {}).get("display_name")
    topic.field_name = (payload.get("field") or {}).get("display_name")
    topic.subfield_name = (payload.get("subfield") or {}).get("display_name")
    topic.keywords_cache = ", ".join(item.get("display_name", "") for item in keywords if item.get("display_name"))
    db.flush()
    return topic, created


def upsert_publication(db: Session, payload: dict) -> tuple[Publication, bool]:
    openalex_id = payload["id"]
    publication = db.query(Publication).filter(Publication.openalex_id == openalex_id).first()
    created = publication is None
    if publication is None:
        publication = Publication(openalex_id=openalex_id, title=payload.get("display_name") or "Untitled")
        db.add(publication)

    abstract_text = reconstruct_abstract(payload.get("abstract_inverted_index"))
    normalized_title = normalize_text(payload.get("display_name"))
    keywords = extract_keywords(payload.get("display_name"), abstract_text)

    publication.title = payload.get("display_name") or publication.title
    publication.normalized_title = normalized_title
    publication.abstract_text = abstract_text
    publication.abstract_summary = summarize_text(abstract_text)
    publication.publication_year = payload.get("publication_year")
    publication.publication_date = payload.get("publication_date")
    publication.cited_by_count = payload.get("cited_by_count") or 0
    publication.doi = payload.get("doi")
    publication.type = payload.get("type")
    publication.language = payload.get("language")
    publication.primary_location_source = (
        ((payload.get("primary_location") or {}).get("source") or {}).get("display_name")
    )
    publication.open_access_url = ((payload.get("open_access") or {}).get("oa_url"))
    publication.keywords_cache = ", ".join(keywords)
    publication.raw_json = json.dumps(payload, ensure_ascii=False)
    db.flush()
    return publication, created


def sync_publication_relations(db: Session, publication: Publication, payload: dict) -> None:
    existing_author_ids = {item.author_id for item in publication.author_links}
    for authorship in payload.get("authorships") or []:
        author_payload = authorship.get("author")
        if not author_payload or not author_payload.get("id"):
            continue
        author, _ = upsert_author(
            db,
            author_payload | {"last_known_institutions": authorship.get("institutions") or []},
        )
        if author.id not in existing_author_ids:
            db.add(
                PublicationAuthor(
                    publication_id=publication.id,
                    author_id=author.id,
                    author_position=authorship.get("author_position"),
                    is_corresponding=authorship.get("is_corresponding"),
                )
            )

    existing_topic_ids = {item.topic_id for item in publication.topic_links}
    for topic_payload in payload.get("topics") or []:
        if not topic_payload.get("id"):
            continue
        topic, _ = upsert_topic(db, topic_payload)
        if topic.id not in existing_topic_ids:
            db.add(
                PublicationTopic(
                    publication_id=publication.id,
                    topic_id=topic.id,
                    score=topic_payload.get("score"),
                )
            )

    db.flush()


def ingest_works(
    db: Session,
    *,
    search: str | None,
    filter: str | None,
    per_page: int,
    pages: int,
    use_cursor: bool,
    select: str | None = None,
) -> IngestionJob:
    client = OpenAlexClient()
    job = start_ingestion_job(
        db,
        entity_type="works",
        query_text=search,
        filters_json={"filter": filter, "per_page": per_page, "pages": pages, "cursor": use_cursor},
    )

    inserted_count = 0
    updated_count = 0
    processed_count = 0
    try:
        works = client.iterate_entities(
            "works",
            search=search,
            filter=filter,
            select=select or WORKS_SELECT,
            per_page=per_page,
            pages=pages,
            use_cursor=use_cursor,
        )
        for payload in works:
            publication, created = upsert_publication(db, payload)
            if created:
                inserted_count += 1
            else:
                updated_count += 1
            sync_publication_relations(db, publication, payload)
            processed_count += 1

        db.commit()
        return finish_job(
            db,
            job,
            status="completed",
            page_count=pages,
            processed_count=processed_count,
            inserted_count=inserted_count,
            updated_count=updated_count,
        )
    except Exception as exc:
        db.rollback()
        return finish_job(
            db,
            job,
            status="failed",
            page_count=pages,
            processed_count=processed_count,
            inserted_count=inserted_count,
            updated_count=updated_count,
            error_message=str(exc),
        )


def ingest_authors(
    db: Session,
    *,
    search: str | None,
    filter: str | None,
    per_page: int,
    pages: int,
    use_cursor: bool,
) -> IngestionJob:
    client = OpenAlexClient()
    job = start_ingestion_job(
        db,
        entity_type="authors",
        query_text=search,
        filters_json={"filter": filter, "per_page": per_page, "pages": pages, "cursor": use_cursor},
    )
    inserted_count = 0
    updated_count = 0
    processed_count = 0
    try:
        authors = client.iterate_entities(
            "authors",
            search=search,
            filter=filter,
            select=AUTHORS_SELECT,
            per_page=per_page,
            pages=pages,
            use_cursor=use_cursor,
        )
        for payload in authors:
            _, created = upsert_author(db, payload)
            inserted_count += int(created)
            updated_count += int(not created)
            processed_count += 1
        db.commit()
        return finish_job(
            db,
            job,
            status="completed",
            page_count=pages,
            processed_count=processed_count,
            inserted_count=inserted_count,
            updated_count=updated_count,
        )
    except Exception as exc:
        db.rollback()
        return finish_job(
            db,
            job,
            status="failed",
            page_count=pages,
            processed_count=processed_count,
            inserted_count=inserted_count,
            updated_count=updated_count,
            error_message=str(exc),
        )


def ingest_topics(
    db: Session,
    *,
    search: str | None,
    filter: str | None,
    per_page: int,
    pages: int,
    use_cursor: bool,
) -> IngestionJob:
    client = OpenAlexClient()
    job = start_ingestion_job(
        db,
        entity_type="topics",
        query_text=search,
        filters_json={"filter": filter, "per_page": per_page, "pages": pages, "cursor": use_cursor},
    )
    inserted_count = 0
    updated_count = 0
    processed_count = 0
    try:
        topics = client.iterate_entities(
            "topics",
            search=search,
            filter=filter,
            select=TOPICS_SELECT,
            per_page=per_page,
            pages=pages,
            use_cursor=use_cursor,
        )
        for payload in topics:
            _, created = upsert_topic(db, payload)
            inserted_count += int(created)
            updated_count += int(not created)
            processed_count += 1
        db.commit()
        return finish_job(
            db,
            job,
            status="completed",
            page_count=pages,
            processed_count=processed_count,
            inserted_count=inserted_count,
            updated_count=updated_count,
        )
    except Exception as exc:
        db.rollback()
        return finish_job(
            db,
            job,
            status="failed",
            page_count=pages,
            processed_count=processed_count,
            inserted_count=inserted_count,
            updated_count=updated_count,
            error_message=str(exc),
        )
