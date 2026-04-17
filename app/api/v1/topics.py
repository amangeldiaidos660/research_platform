from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import TopicDetailRead, TopicSlimRead
from app.services.repository_service import get_topic_detail, list_topics

router = APIRouter()


@router.get("", response_model=list[TopicSlimRead], summary="List topics")
async def read_topics(
    q: str | None = None,
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[TopicSlimRead]:
    items = list_topics(db, q=q, limit=limit)
    return [TopicSlimRead.model_validate(item) for item in items]


@router.get("/{topic_id}", response_model=TopicDetailRead, summary="Get topic detail")
async def read_topic_detail(
    topic_id: int,
    db: Session = Depends(get_db),
) -> TopicDetailRead:
    topic = get_topic_detail(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    return TopicDetailRead.model_validate(topic)
