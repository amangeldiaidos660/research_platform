from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.personalization import SavedSearchCreate, SavedSearchRead
from app.services.personalization_service import create_saved_search, list_saved_searches

router = APIRouter()


@router.get("", response_model=list[SavedSearchRead], summary="List saved searches")
async def read_saved_searches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SavedSearchRead]:
    items = list_saved_searches(db, current_user)
    return [SavedSearchRead.model_validate(item) for item in items]


@router.post("", response_model=SavedSearchRead, status_code=status.HTTP_201_CREATED)
async def create_saved_search_endpoint(
    payload: SavedSearchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedSearchRead:
    item = create_saved_search(db, current_user, payload)
    return SavedSearchRead.model_validate(item)

