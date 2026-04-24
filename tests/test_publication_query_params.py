import os
from collections.abc import Generator
from typing import Any

os.environ.setdefault("AUTO_CREATE_TABLES", "false")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.v1 import pages as pages_module  # noqa: E402
from app.api.v1 import publications as publications_module  # noqa: E402
from app.db.session import get_db  # noqa: E402


def override_db() -> Generator[object, None, None]:
    yield object()


def create_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(pages_module.router)
    app.include_router(publications_module.router, prefix="/api/v1/publications")
    app.dependency_overrides[get_db] = override_db
    return TestClient(app)


def test_publications_api_ignores_empty_optional_int_filters(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_list_publications(db: object, **kwargs: Any) -> list[Any]:
        captured.update(kwargs)
        return []

    monkeypatch.setattr(publications_module, "list_publications", fake_list_publications)

    response = create_test_client().get(
        "/api/v1/publications?q=mental+health&year=&topic_id=&author_id=&sort=recent"
    )

    assert response.status_code == 200
    assert response.json() == []
    assert captured["year"] is None
    assert captured["topic_id"] is None
    assert captured["author_id"] is None


def test_publications_page_ignores_empty_optional_int_filters(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_list_publications(db: object, **kwargs: Any) -> list[Any]:
        captured.update(kwargs)
        return []

    monkeypatch.setattr(pages_module, "list_publications", fake_list_publications)
    monkeypatch.setattr(pages_module, "list_topics", lambda db, limit: [])
    monkeypatch.setattr(pages_module, "list_authors", lambda db, limit: [])

    response = create_test_client().get(
        "/publications?q=mental+health&year=&topic_id=&author_id=&sort=recent"
    )

    assert response.status_code == 200
    assert captured["year"] is None
    assert captured["topic_id"] is None
    assert captured["author_id"] is None
