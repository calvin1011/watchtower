"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from .env or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
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

    # Scraping
    serpapi_key: str | None = None

    # Email
    resend_api_key: str | None = None
    digest_recipient: str = "jindou@happy.co"


settings = Settings()
