from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database
    database_url: str = "mysql+pymysql://root@127.0.0.1:3306/speech_to_summary"

    # Auth
    secret_key: str = "thisIsVeryVerySecure!!!"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI Provider
    ai_provider: str = "groq"  # "openai" or "groq"
    openai_api_key: str | None = None
    groq_api_key: str | None = None

    # App
    app_name: str = "Voice Summary API"
    app_version: str = "0.2.0"
    debug: bool = True
    cors_origins: list[str] = ["*"]

    # Audio
    max_audio_duration_ms: int = 2 * 60 * 1000  # 2 minutes
    max_file_size_mb: int = 25
    temp_dir: str = "/tmp"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
