from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.models import *  # noqa: F401,F403
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(api_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
