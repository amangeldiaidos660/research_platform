from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.personalization import FavoriteCreate, FavoriteRead
from app.services.personalization_service import add_favorite, list_favorites, remove_favorite

router = APIRouter()


@router.get("", response_model=list[FavoriteRead], summary="List favorite publications")
async def read_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FavoriteRead]:
    favorites = list_favorites(db, current_user)
    return [FavoriteRead.model_validate(item) for item in favorites]


@router.post("", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    payload: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteRead:
    favorite = add_favorite(db, current_user, payload)
    return FavoriteRead.model_validate(favorite)


@router.delete("/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    remove_favorite(db, current_user, publication_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

