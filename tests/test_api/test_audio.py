"""Tests for audio API endpoints."""

from fastapi.testclient import TestClient
from unittest.mock import patch


class TestAudioAPI:
    def test_upload_requires_auth(self, client: TestClient):
        resp = client.post("/user/audio/upload")
        assert resp.status_code == 401

    def test_upload_rejects_non_audio(self, client: TestClient, auth_headers):
        resp = client.post(
            "/user/audio/upload",
            files={"file": ("test.txt", b"hello world", "text/plain")},
            params={"prompt": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_upload_with_audio_mime(self, client: TestClient, auth_headers):
        """Test that audio MIME type passes validation (AI call will fail, but validation passes)."""
        with patch("app.services.audio_service.AudioService.upload_and_transcribe") as mock:
            mock.return_value = {"filename": "test.mp3", "transcript": "mock", "id": 1}
            resp = client.post(
                "/user/audio/upload",
                files={"file": ("test.mp3", b"fakeaudio", "audio/mpeg")},
                params={"prompt": ""},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_list_audio(self, client: TestClient, auth_headers):
        resp = client.get("/user/audio/", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_get_audio_summaries(self, client: TestClient, auth_headers):
        resp = client.get("/user/audio/1", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
