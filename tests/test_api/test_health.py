"""Tests for health endpoint."""

from fastapi.testclient import TestClient


class TestHealth:
    def test_health_check(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["api"] is not None
        assert body["timestamp"] is not None

    def test_health_without_db(self, client: TestClient):
        resp = client.get("/health?include_db=false")
        assert resp.status_code == 200
        body = resp.json()
        assert "api" in body
        assert "database" not in body

    def test_root_redirects_to_docs(self, client: TestClient):
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 307  # Temporary redirect
        assert "/docs" in resp.headers["location"]
