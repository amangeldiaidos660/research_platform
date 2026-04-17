from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import AuthorDetailRead, AuthorRead, PublicationRead
from app.services.repository_service import get_author_detail, list_authors

router = APIRouter()


@router.get("", response_model=list[AuthorRead], summary="List authors")
async def read_authors(
    q: str | None = None,
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[AuthorRead]:
    items = list_authors(db, q=q, limit=limit)
    return [AuthorRead.model_validate(item) for item in items]


@router.get("/{author_id}", response_model=AuthorDetailRead, summary="Get author detail")
async def read_author_detail(
    author_id: int,
    db: Session = Depends(get_db),
) -> AuthorDetailRead:
    author = get_author_detail(db, author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    data = AuthorDetailRead.model_validate(author).model_dump()
    data["publications"] = [
        PublicationRead.model_validate(link.publication).model_dump() for link in author.publication_links
    ]
    return AuthorDetailRead(**data)
