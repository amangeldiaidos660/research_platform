from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.query_params import parse_optional_int_query
from app.db.session import get_db
from app.schemas.domain import AuthorRead, PublicationDetailRead, PublicationRead, TopicSlimRead
from app.services.repository_service import get_publication_detail, list_publications

router = APIRouter()


@router.get("", response_model=list[PublicationRead], summary="List publications")
async def read_publications(
    q: str | None = None,
    year: str | None = None,
    topic_id: str | None = None,
    author_id: str | None = None,
    sort: str = Query(default="recent", pattern="^(recent|citations)$"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[PublicationRead]:
    parsed_year = parse_optional_int_query(year, "year")
    parsed_topic_id = parse_optional_int_query(topic_id, "topic_id")
    parsed_author_id = parse_optional_int_query(author_id, "author_id")
    items = list_publications(
        db,
        q=q,
        year=parsed_year,
        topic_id=parsed_topic_id,
        author_id=parsed_author_id,
        sort=sort,
        limit=limit,
    )
    return [PublicationRead.model_validate(item) for item in items]


@router.get("/{publication_id}", response_model=PublicationDetailRead, summary="Get publication detail")
async def read_publication_detail(
    publication_id: int,
    db: Session = Depends(get_db),
) -> PublicationDetailRead:
    publication = get_publication_detail(db, publication_id)
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    data = PublicationDetailRead.model_validate(publication).model_dump()
    data["authors"] = [AuthorRead.model_validate(link.author).model_dump() for link in publication.author_links]
    data["topics"] = [TopicSlimRead.model_validate(link.topic).model_dump() for link in publication.topic_links]
    return PublicationDetailRead(**data)
