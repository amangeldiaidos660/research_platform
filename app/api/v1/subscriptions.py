from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.personalization import TopicSubscriptionCreate, TopicSubscriptionRead
from app.services.personalization_service import create_topic_subscription, list_topic_subscriptions

router = APIRouter()


@router.get("", response_model=list[TopicSubscriptionRead], summary="List topic subscriptions")
async def read_topic_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TopicSubscriptionRead]:
    items = list_topic_subscriptions(db, current_user)
    return [TopicSubscriptionRead.model_validate(item) for item in items]


@router.post("", response_model=TopicSubscriptionRead, status_code=status.HTTP_201_CREATED)
async def create_topic_subscription_endpoint(
    payload: TopicSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TopicSubscriptionRead:
    item = create_topic_subscription(db, current_user, payload)
    return TopicSubscriptionRead.model_validate(item)

