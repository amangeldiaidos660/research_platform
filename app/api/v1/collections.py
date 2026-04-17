from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.personalization import (
    CollectionCreate,
    CollectionItemCreate,
    CollectionRead,
)
from app.services.personalization_service import (
    add_collection_item,
    create_collection,
    list_collections,
)

router = APIRouter()


@router.get("", response_model=list[CollectionRead], summary="List collections")
async def read_collections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CollectionRead]:
    collections = list_collections(db, current_user)
    return [CollectionRead.model_validate(item) for item in collections]


@router.post("", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def create_collection_endpoint(
    payload: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionRead:
    collection = create_collection(db, current_user, payload)
    return CollectionRead.model_validate(collection)


@router.post("/{collection_id}/items", response_model=CollectionRead, status_code=status.HTTP_201_CREATED)
async def add_collection_item_endpoint(
    collection_id: int,
    payload: CollectionItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CollectionRead:
    collection = add_collection_item(db, current_user, collection_id, payload)
    return CollectionRead.model_validate(collection)

