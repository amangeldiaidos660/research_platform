from fastapi import APIRouter

router = APIRouter()


@router.get("/status", summary="Auth module status")
async def auth_status() -> dict[str, str]:
    return {
        "module": "auth",
        "status": "planned",
        "next_step": "JWT, registration, login, personalization models",
    }

