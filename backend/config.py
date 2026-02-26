"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Look for .env in backend/ and project root (when running from backend/)
_env_files = [".env", str(Path(__file__).resolve().parent.parent / ".env")]


class Settings(BaseSettings):
    """Settings loaded from .env or environment variables."""

    model_config = SettingsConfigDict(
        env_file=_env_files,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    port: int = 8000

    # Database
    database_url: str | None = None

    # AI
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # Scraping
    serpapi_key: str | None = None

    # Email
    resend_api_key: str | None = None
    digest_recipient: str = "jindou@happy.co"


settings = Settings()
