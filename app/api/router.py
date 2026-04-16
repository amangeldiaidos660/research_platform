from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.pages import router as pages_router

api_router = APIRouter()
api_router.include_router(pages_router, tags=["Pages"])
api_router.include_router(health_router, prefix="/api/v1", tags=["Health"])
api_router.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])

