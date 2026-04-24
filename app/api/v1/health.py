from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Author, IngestionJob, Publication, Topic
from app.db.session import get_db

router = APIRouter()


@router.get("/health", summary="Service healthcheck")
async def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


@router.get("/metrics", response_class=PlainTextResponse, summary="Prometheus metrics")
async def metrics(db: Session = Depends(get_db)) -> str:
    publications_total = db.query(func.count(Publication.id)).scalar() or 0
    authors_total = db.query(func.count(Author.id)).scalar() or 0
    topics_total = db.query(func.count(Topic.id)).scalar() or 0
    ingestion_jobs_total = db.query(func.count(IngestionJob.id)).scalar() or 0
    return "\n".join(
        [
            "# HELP rip_publications_total Total publications in catalog",
            "# TYPE rip_publications_total gauge",
            f"rip_publications_total {publications_total}",
            "# HELP rip_authors_total Total authors in catalog",
            "# TYPE rip_authors_total gauge",
            f"rip_authors_total {authors_total}",
            "# HELP rip_topics_total Total topics in catalog",
            "# TYPE rip_topics_total gauge",
            f"rip_topics_total {topics_total}",
            "# HELP rip_ingestion_jobs_total Total ingestion jobs",
            "# TYPE rip_ingestion_jobs_total counter",
            f"rip_ingestion_jobs_total {ingestion_jobs_total}",
            "",
        ]
    )
