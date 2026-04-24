from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router import api_router
from app.db.models import Author, Publication, Topic
from app.db.session import get_db


def test_prometheus_metrics_endpoint(db_session) -> None:
    db_session.add(Publication(openalex_id="W1", title="Paper", cited_by_count=3))
    db_session.add(Author(openalex_id="A1", display_name="Author"))
    db_session.add(Topic(openalex_id="T1", name="Topic"))
    db_session.commit()

    app = FastAPI()
    app.include_router(api_router)

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    response = TestClient(app).get("/api/v1/metrics")

    assert response.status_code == 200
    assert "rip_publications_total 1" in response.text
    assert "rip_authors_total 1" in response.text
    assert "rip_topics_total 1" in response.text
