"""Tests for prompt API endpoints."""

from fastapi.testclient import TestClient


class TestAdminPromptAPI:
    def test_create_prompt(self, client: TestClient, admin_headers):
        resp = client.post("/admin/prompt/", params={
            "title": "New Prompt", "content": "Summarize this",
        }, headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["title"] == "New Prompt"

    def test_create_prompt_requires_admin(self, client: TestClient, auth_headers):
        resp = client.post("/admin/prompt/", params={
            "title": "Hack", "content": "Should fail",
        }, headers=auth_headers)
        # FastAPI raises HTTPException 403 before route handler runs
        assert resp.status_code == 403
        assert "Admin access required" in resp.text

    def test_list_prompts(self, client: TestClient, admin_headers, test_prompt):
        resp = client.get("/admin/prompt/", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert len(body["data"]) >= 1

    def test_update_prompt(self, client: TestClient, admin_headers, test_prompt):
        resp = client.put(f"/admin/prompt/{test_prompt.id}", params={
            "title": "Updated", "content": "New content",
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "Updated"

    def test_soft_delete_and_restore(self, client: TestClient, admin_headers, test_prompt):
        # Delete
        client.patch(f"/admin/prompt/{test_prompt.id}/delete", headers=admin_headers)
        list_resp = client.get("/admin/prompt/?include_deleted=false", headers=admin_headers)
        ids = [p["id"] for p in list_resp.json()["data"]]
        assert test_prompt.id not in ids

        # Restore
        client.patch(f"/admin/prompt/{test_prompt.id}/restore", headers=admin_headers)
        list_resp2 = client.get("/admin/prompt/?include_deleted=false", headers=admin_headers)
        ids2 = [p["id"] for p in list_resp2.json()["data"]]
        assert test_prompt.id in ids2


class TestUserPromptAPI:
    def test_user_list_prompts(self, client: TestClient, auth_headers, test_prompt):
        resp = client.get("/user/prompt/", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
