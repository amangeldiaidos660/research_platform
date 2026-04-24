from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.openalex import IngestRequest, IngestionJobRead, OpenAlexListQuery
from app.services.collector_service import ingest_authors, ingest_topics, ingest_works
from app.services.openalex_client import OpenAlexClient
from app.services.repository_service import list_ingestion_jobs

router = APIRouter()


@router.get("/jobs", response_model=list[IngestionJobRead], summary="List ingestion jobs")
async def read_ingestion_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[IngestionJobRead]:
    return [IngestionJobRead.model_validate(item) for item in list_ingestion_jobs(db, limit=limit)]


@router.get("/refresh-defaults", response_model=list[IngestionJobRead], summary="Refresh default topics")
async def refresh_default_topics(db: Session = Depends(get_db)) -> list[IngestionJobRead]:
    current_year = datetime.now(UTC).year
    jobs = [
        ingest_works(
            db,
            search=query,
            filter=f"publication_year:{current_year}",
            per_page=25,
            pages=1,
            use_cursor=False,
            sort="publication_date:desc",
            select=None,
        )
        for query in ("mental health", "climate change", "machine learning")
    ]
    return [IngestionJobRead.model_validate(job) for job in jobs]


@router.get("/openalex/{entity}", summary="Proxy list query to OpenAlex")
async def proxy_openalex_list(
    entity: str,
    search: str | None = None,
    filter: str | None = None,
    select: str | None = None,
    sort: str | None = None,
    per_page: int = Query(default=25, ge=1, le=100),
    page: int = Query(default=1, ge=1),
) -> dict:
    OpenAlexListQuery(
        search=search,
        filter=filter,
        select=select,
        sort=sort,
        per_page=per_page,
        page=page,
    )
    client = OpenAlexClient()
    return client.list_entities(
        entity,
        search=search,
        filter=filter,
        select=select,
        sort=sort,
        per_page=per_page,
        page=page,
    )


@router.get("/openalex/{entity}/{openalex_id:path}", summary="Proxy detail query to OpenAlex")
async def proxy_openalex_detail(
    entity: str,
    openalex_id: str,
    select: str | None = None,
) -> dict:
    client = OpenAlexClient()
    return client.get_entity(entity, openalex_id, select=select)


@router.post("/works", response_model=IngestionJobRead, status_code=status.HTTP_201_CREATED)
async def ingest_works_endpoint(
    payload: IngestRequest,
    db: Session = Depends(get_db),
) -> IngestionJobRead:
    job = ingest_works(
        db,
        search=payload.search,
        filter=payload.filter,
        sort=payload.sort,
        per_page=payload.per_page,
        pages=payload.pages,
        use_cursor=payload.cursor,
        select=payload.select,
    )
    return IngestionJobRead.model_validate(job)


@router.post("/authors", response_model=IngestionJobRead, status_code=status.HTTP_201_CREATED)
async def ingest_authors_endpoint(
    payload: IngestRequest,
    db: Session = Depends(get_db),
) -> IngestionJobRead:
    job = ingest_authors(
        db,
        search=payload.search,
        filter=payload.filter,
        per_page=payload.per_page,
        pages=payload.pages,
        use_cursor=payload.cursor,
    )
    return IngestionJobRead.model_validate(job)


@router.post("/topics", response_model=IngestionJobRead, status_code=status.HTTP_201_CREATED)
async def ingest_topics_endpoint(
    payload: IngestRequest,
    db: Session = Depends(get_db),
) -> IngestionJobRead:
    job = ingest_topics(
        db,
        search=payload.search,
        filter=payload.filter,
        per_page=payload.per_page,
        pages=payload.pages,
        use_cursor=payload.cursor,
    )
    return IngestionJobRead.model_validate(job)
