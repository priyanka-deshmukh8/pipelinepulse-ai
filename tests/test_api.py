import os
os.environ["DATABASE_URL"] = "sqlite:///./test_pipelinepulse.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-tests"
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.db import Base, engine

@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "engineer@example.com",
        "password": "test-password-12345"
    })
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_incidents_require_auth(client):
    response = client.post("/api/v1/incidents", json={
        "pipeline_name": "daily-sales-load", "error_message": "bad cast"
    })
    assert response.status_code == 401

def test_create_and_get_incident(client, auth_headers):
    created = client.post("/api/v1/incidents", headers=auth_headers, json={
        "pipeline_name": "daily-sales-load",
        "error_message": "CAST_INVALID_INPUT: empty string cannot be cast to INT"
    })
    assert created.status_code == 201
    incident_id = created.json()["id"]
    fetched = client.get(f"/api/v1/incidents/{incident_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["pipeline_name"] == "daily-sales-load"

def test_analyze_incident(client, auth_headers):
    created = client.post("/api/v1/incidents", headers=auth_headers, json={
        "pipeline_name": "daily-sales-load",
        "error_message": "CAST_INVALID_INPUT: empty string cannot be cast to INT"
    })
    incident_id = created.json()["id"]
    response = client.post(f"/api/v1/incidents/{incident_id}/analyze", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["failure_category"] == "schema_or_data_quality"
    assert response.json()["requires_human_review"] is True
    assert response.json()["remediation_steps"]

def test_retry_count(client, auth_headers):
    created = client.post("/api/v1/incidents", headers=auth_headers, json={
        "pipeline_name": "cluster-job", "error_message": "cluster terminated unexpectedly"
    })
    incident_id = created.json()["id"]
    response = client.post(
        f"/api/v1/incidents/{incident_id}/retry-count",
        headers=auth_headers, json={"increment_by": 2}
    )
    assert response.status_code == 200
    assert response.json()["retry_count"] == 2
