"""Tests for provider factory."""

from unittest.mock import patch
from app.providers.factory import create_provider
from app.providers.base import AIProvider
from app.providers.factory import OpenAICompatibleProvider


class TestProviderFactory:
    def test_create_groq_provider(self):
        with patch("app.providers.factory.settings") as mock_settings:
            mock_settings.ai_provider = "groq"
            mock_settings.groq_api_key = "gsk_test_key"
            provider = create_provider()
            assert isinstance(provider, OpenAICompatibleProvider)

    def test_create_openai_provider(self):
        with patch("app.providers.factory.settings") as mock_settings:
            mock_settings.ai_provider = "openai"
            mock_settings.openai_api_key = "sk-test-key"
            provider = create_provider()
            assert isinstance(provider, OpenAICompatibleProvider)

    def test_groq_missing_key_raises(self):
        with patch("app.providers.factory.settings") as mock_settings:
            mock_settings.ai_provider = "groq"
            mock_settings.groq_api_key = None
            import pytest
            from app.core.exceptions import ServiceError
            with pytest.raises(ServiceError):
                create_provider()
