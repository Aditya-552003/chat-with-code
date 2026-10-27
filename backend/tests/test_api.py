"""Tests for the FastAPI application endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_does_not_expose_keys(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        # Should not contain actual key values
        assert "GEMINI_API_KEY" not in str(data)
        assert "GITHUB_TOKEN" not in str(data)


class TestRepositoryEndpoints:
    def test_load_invalid_url(self, client):
        resp = client.post("/api/repositories/load", json={
            "repository_url": "https://gitlab.com/owner/repo"
        })
        assert resp.status_code in (400, 422)

    def test_load_missing_url(self, client):
        resp = client.post("/api/repositories/load", json={})
        assert resp.status_code == 422

    def test_get_nonexistent_repo(self, client):
        resp = client.get("/api/repositories/nonexistent-repo-id")
        assert resp.status_code == 404

    def test_get_nonexistent_job(self, client):
        resp = client.get("/api/repositories/jobs/nonexistent-job-id")
        assert resp.status_code == 404


class TestChatEndpoints:
    def test_chat_without_index(self, client):
        resp = client.post("/api/chat", json={
            "repository_id": "nonexistent",
            "message": "What does this repo do?"
        })
        assert resp.status_code == 409

    def test_chat_empty_message(self, client):
        resp = client.post("/api/chat", json={
            "repository_id": "test",
            "message": ""
        })
        assert resp.status_code == 422


class TestConversationEndpoints:
    def test_get_nonexistent_conversation(self, client):
        resp = client.get("/api/conversations/nonexistent")
        assert resp.status_code == 404

    def test_list_conversations(self, client):
        resp = client.get("/api/conversations")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_export_nonexistent(self, client):
        resp = client.get("/api/conversations/nonexistent/export")
        assert resp.status_code == 404


class TestCORS:
    def test_cors_preflight(self, client):
        resp = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200
