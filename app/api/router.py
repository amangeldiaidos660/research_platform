from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.authors import router as authors_router
from app.api.v1.auth import router as auth_router
from app.api.v1.collections import router as collections_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.health import router as health_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.me import router as me_router
from app.api.v1.pages import router as pages_router
from app.api.v1.publications import router as publications_router
from app.api.v1.saved_searches import router as saved_searches_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.topics import router as topics_router

api_router = APIRouter()
api_router.include_router(pages_router, tags=["Pages"])
api_router.include_router(health_router, prefix="/api/v1", tags=["Health"])
api_router.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
api_router.include_router(me_router, prefix="/api/v1", tags=["Users"])
api_router.include_router(favorites_router, prefix="/api/v1/favorites", tags=["Favorites"])
api_router.include_router(
    saved_searches_router,
    prefix="/api/v1/saved-searches",
    tags=["Saved Searches"],
)
api_router.include_router(collections_router, prefix="/api/v1/collections", tags=["Collections"])
api_router.include_router(
    subscriptions_router,
    prefix="/api/v1/subscriptions",
    tags=["Subscriptions"],
)
api_router.include_router(publications_router, prefix="/api/v1/publications", tags=["Publications"])
api_router.include_router(authors_router, prefix="/api/v1/authors", tags=["Authors"])
api_router.include_router(topics_router, prefix="/api/v1/topics", tags=["Topics"])
api_router.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
api_router.include_router(ingestion_router, prefix="/api/v1/ingestion", tags=["Ingestion"])
