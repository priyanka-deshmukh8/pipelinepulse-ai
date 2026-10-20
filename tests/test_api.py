import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure tests use an isolated SQLite database before importing the app.
os.environ["DATABASE_URL"] = "sqlite:///./test_pipelinepulse.db"
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

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_and_get_incident(client):
    created = client.post("/api/v1/incidents", json={
        "pipeline_name": "daily-sales-load",
        "error_message": "CAST_INVALID_INPUT: empty string cannot be cast to INT"
    })
    assert created.status_code == 201
    incident_id = created.json()["id"]
    fetched = client.get(f"/api/v1/incidents/{incident_id}")
    assert fetched.status_code == 200
    assert fetched.json()["pipeline_name"] == "daily-sales-load"

def test_analyze_incident(client):
    created = client.post("/api/v1/incidents", json={
        "pipeline_name": "daily-sales-load",
        "error_message": "CAST_INVALID_INPUT: empty string cannot be cast to INT"
    })
    incident_id = created.json()["id"]
    response = client.post(f"/api/v1/incidents/{incident_id}/analyze")
    assert response.status_code == 200
    assert response.json()["failure_category"] == "schema_or_data_quality"
    assert response.json()["requires_human_review"] is True
    assert response.json()["remediation_steps"]

def test_retry_count(client):
    created = client.post("/api/v1/incidents", json={
        "pipeline_name": "cluster-job",
        "error_message": "cluster terminated unexpectedly"
    })
    incident_id = created.json()["id"]
    response = client.post(f"/api/v1/incidents/{incident_id}/retry-count", json={"increment_by": 2})
    assert response.status_code == 200
    assert response.json()["retry_count"] == 2
