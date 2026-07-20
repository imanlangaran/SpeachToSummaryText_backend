"""Tests for auth API endpoints."""

from fastapi.testclient import TestClient


class TestAuthAPI:
    def test_register_success(self, client: TestClient):
        resp = client.post("/auth/register", json={
            "email": "fresh@test.com", "password": "secure123",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["email"] == "fresh@test.com"
        assert body["error"] is None

    def test_register_duplicate(self, client: TestClient, test_user):
        resp = client.post("/auth/register", json={
            "email": test_user.email, "password": "any",
        })
        assert resp.status_code == 200  # Still 200 (standard envelope)
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == "DUPLICATE"

    def test_login_success(self, client: TestClient, test_user):
        resp = client.post("/auth/login", json={
            "email": "user@test.com", "password": "password123",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "access_token" in body["data"]

    def test_login_wrong_password(self, client: TestClient, test_user):
        resp = client.post("/auth/login", json={
            "email": "user@test.com", "password": "wrong",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTH_ERROR"

    def test_login_swagger(self, client: TestClient, test_user):
        resp = client.post("/auth/loginSwagger", data={
            "username": "user@test.com", "password": "password123",
        })
        assert resp.status_code == 200
        body = resp.json()
        # Swagger endpoint returns flat token (not wrapped in envelope)
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_me_authenticated(self, client: TestClient, auth_headers):
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["email"] == "user@test.com"

    def test_me_unauthenticated(self, client: TestClient):
        resp = client.get("/auth/me")
        assert resp.status_code == 401
