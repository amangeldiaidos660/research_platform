from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.services.analytics_service import get_dashboard_analytics, get_topic_growth
from app.services.repository_service import (
    dashboard_counts,
    get_author_detail,
    get_publication_detail,
    get_topic_detail,
    list_authors,
    list_ingestion_jobs,
    list_publications,
    list_topics,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("app/templates")))


def base_context(request: Request) -> dict:
    return {"request": request, "app_name": settings.app_name}


@router.get("/", response_class=HTMLResponse, summary="Home page")
async def home(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    analytics = get_dashboard_analytics(db)
    recent_jobs = list_ingestion_jobs(db, limit=5)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=base_context(request)
        | {
            "analytics": analytics,
            "recent_jobs": recent_jobs,
        },
    )


@router.get("/publications", response_class=HTMLResponse)
async def publications_page(
    request: Request,
    q: str | None = None,
    year: int | None = None,
    topic_id: int | None = None,
    author_id: int | None = None,
    sort: str = Query(default="recent"),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    items = list_publications(db, q=q, year=year, topic_id=topic_id, author_id=author_id, sort=sort, limit=50)
    topics = list_topics(db, limit=100)
    authors = list_authors(db, limit=100)
    return templates.TemplateResponse(
        request=request,
        name="publications.html",
        context=base_context(request)
        | {"publications": items, "topics": topics, "authors": authors, "filters": {"q": q, "year": year, "topic_id": topic_id, "author_id": author_id, "sort": sort}},
    )


@router.get("/publications/{publication_id}", response_class=HTMLResponse)
async def publication_detail_page(
    request: Request,
    publication_id: int,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    publication = get_publication_detail(db, publication_id)
    return templates.TemplateResponse(
        request=request,
        name="publication_detail.html",
        context=base_context(request) | {"publication": publication},
    )


@router.get("/authors", response_class=HTMLResponse)
async def authors_page(
    request: Request,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    items = list_authors(db, q=q, limit=100)
    return templates.TemplateResponse(
        request=request,
        name="authors.html",
        context=base_context(request) | {"authors": items, "q": q},
    )


@router.get("/authors/{author_id}", response_class=HTMLResponse)
async def author_detail_page(
    request: Request,
    author_id: int,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    author = get_author_detail(db, author_id)
    return templates.TemplateResponse(
        request=request,
        name="author_detail.html",
        context=base_context(request) | {"author": author},
    )


@router.get("/topics", response_class=HTMLResponse)
async def topics_page(
    request: Request,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    items = list_topics(db, q=q, limit=100)
    return templates.TemplateResponse(
        request=request,
        name="topics.html",
        context=base_context(request) | {"topics": items, "q": q},
    )


@router.get("/topics/{topic_id}", response_class=HTMLResponse)
async def topic_detail_page(
    request: Request,
    topic_id: int,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    topic = get_topic_detail(db, topic_id)
    growth = get_topic_growth(db, topic_id)
    related_publications = list_publications(db, topic_id=topic_id, limit=20, sort="citations")
    return templates.TemplateResponse(
        request=request,
        name="topic_detail.html",
        context=base_context(request)
        | {"topic": topic, "growth": growth, "related_publications": related_publications},
    )


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    analytics = get_dashboard_analytics(db)
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context=base_context(request) | {"analytics": analytics},
    )


@router.get("/ingestion", response_class=HTMLResponse)
async def ingestion_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    jobs = list_ingestion_jobs(db, limit=20)
    counts = dashboard_counts(db)
    return templates.TemplateResponse(
        request=request,
        name="ingestion.html",
        context=base_context(request) | {"jobs": jobs, "counts": counts},
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context=base_context(request),
    )
