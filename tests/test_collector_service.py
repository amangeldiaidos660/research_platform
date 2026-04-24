from datetime import UTC, datetime, timedelta

from app.db.models import IngestionJob
from app.services.collector_service import (
    should_refresh_ingestion,
    sync_publication_relations,
    upsert_publication,
)


def work_payload() -> dict:
    return {
        "id": "https://openalex.org/W123",
        "doi": "https://doi.org/10.123/example",
        "display_name": "Sleep and memory consolidation",
        "publication_year": 2026,
        "publication_date": "2026-01-10",
        "cited_by_count": 42,
        "type": "article",
        "language": "en",
        "abstract_inverted_index": {"Sleep": [0], "improves": [1], "memory": [2]},
        "open_access": {"oa_url": "https://example.com/article"},
        "primary_location": {"source": {"display_name": "Science Journal"}},
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A1",
                    "display_name": "Ada Researcher",
                    "orcid": None,
                    "works_count": 10,
                    "cited_by_count": 50,
                },
                "institutions": [{"display_name": "Research University"}],
                "author_position": "first",
                "is_corresponding": True,
            }
        ],
        "topics": [
            {
                "id": "https://openalex.org/T1",
                "display_name": "Memory",
                "description": "Memory studies",
                "works_count": 100,
                "cited_by_count": 500,
                "keywords": [{"display_name": "sleep"}],
                "subfield": {"display_name": "Psychology"},
                "field": {"display_name": "Medicine"},
                "domain": {"display_name": "Health Sciences"},
                "score": 0.9,
            }
        ],
    }


def test_upsert_publication_and_relations_are_idempotent(db_session) -> None:
    publication, created = upsert_publication(db_session, work_payload())
    sync_publication_relations(db_session, publication, work_payload())
    db_session.commit()

    assert created is True
    assert publication.cited_by_count == 42
    assert len(publication.author_links) == 1
    assert len(publication.topic_links) == 1

    publication, created = upsert_publication(db_session, work_payload() | {"cited_by_count": 43})
    sync_publication_relations(db_session, publication, work_payload())
    db_session.commit()

    assert created is False
    assert publication.cited_by_count == 43
    assert len(publication.author_links) == 1
    assert len(publication.topic_links) == 1


def test_should_refresh_ingestion_uses_ttl(db_session) -> None:
    db_session.add(
        IngestionJob(
            source="openalex",
            entity_type="works",
            status="completed",
            query_text="mental health",
            filters_json='{"filter": "publication_year:2026"}',
            updated_at=datetime.now(UTC) - timedelta(hours=2),
        )
    )
    db_session.commit()

    assert (
        should_refresh_ingestion(
            db_session,
            entity_type="works",
            query_text="mental health",
            filter="publication_year:2026",
            ttl_hours=24,
        )
        is False
    )
    assert (
        should_refresh_ingestion(
            db_session,
            entity_type="works",
            query_text="mental health",
            filter="publication_year:2026",
            ttl_hours=1,
        )
        is True
    )
