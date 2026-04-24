from datetime import UTC, datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from app.api.router import api_router
from app.db.session import get_db


def supabase_token(email: str = "reader@example.com") -> str:
    return jwt.encode(
        {
            "iss": "https://test.supabase.co/auth/v1",
            "sub": "google-user-id",
            "email": email,
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "user_metadata": {"full_name": "Research Reader"},
        },
        "not-the-app-secret",
        algorithm="HS256",
    )


def client_for(db_session) -> TestClient:
    app = FastAPI()
    app.include_router(api_router)

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {supabase_token()}"}


def publication_payload() -> dict:
    return {
        "publication": {
            "openalex_id": "https://openalex.org/W1",
            "title": "Mental health research",
            "publication_year": 2026,
            "cited_by_count": 12,
            "doi": "https://doi.org/10.1/example",
            "primary_location_source": "Journal",
        }
    }


def test_supabase_user_can_use_personalization_endpoints(db_session) -> None:
    client = client_for(db_session)
    headers = auth_headers()

    me = client.get("/api/v1/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "reader@example.com"

    favorite = client.post("/api/v1/favorites", json=publication_payload(), headers=headers)
    assert favorite.status_code == 201
    assert favorite.json()["publication"]["title"] == "Mental health research"
    assert client.get("/api/v1/favorites", headers=headers).json()[0]["publication"]["openalex_id"]

    saved_search = client.post(
        "/api/v1/saved-searches",
        json={"name": "Mental health", "query": "mental health", "filters_json": {"sort": "citations"}},
        headers=headers,
    )
    assert saved_search.status_code == 201
    assert client.get("/api/v1/saved-searches", headers=headers).json()[0]["query"] == "mental health"

    collection = client.post(
        "/api/v1/collections",
        json={"name": "Literature review", "description": "First reading list"},
        headers=headers,
    )
    assert collection.status_code == 201
    collection_id = collection.json()["id"]
    item = client.post(
        f"/api/v1/collections/{collection_id}/items",
        json=publication_payload(),
        headers=headers,
    )
    assert item.status_code == 201
    assert item.json()["items"][0]["publication"]["title"] == "Mental health research"

    subscription = client.post(
        "/api/v1/subscriptions",
        json={
            "topic": {
                "openalex_id": "https://openalex.org/T1",
                "name": "Mental health",
                "description": None,
                "works_count": 100,
                "keywords_cache": None,
            }
        },
        headers=headers,
    )
    assert subscription.status_code == 201
    assert client.get("/api/v1/subscriptions", headers=headers).json()[0]["topic"]["name"] == "Mental health"
