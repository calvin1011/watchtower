"""Application settings loaded from environment variables."""

import os
import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Look for .env in backend/ and project root (when running from backend/)
_env_files = [".env", str(Path(__file__).resolve().parent.parent / ".env")]

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "SERPAPI_KEY",
    "RESEND_API_KEY",
]


def validate_required_env() -> None:
    """Fail fast at startup if required env vars are missing."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return
    missing = []
    for name in REQUIRED_ENV_VARS:
        # settings is defined below; at call time it exists
        val = getattr(settings, name.lower(), None)
        if not val or (isinstance(val, str) and not val.strip()):
            missing.append(name)
    if missing:
        print("ERROR: Missing required environment variables:", file=sys.stderr)
        for name in missing:
            print(f"  - {name}", file=sys.stderr)
        print("\nCopy .env.example to .env and fill in your values. See docs/SETUP.md", file=sys.stderr)
        sys.exit(1)


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
    cors_origins: str = ""  # Comma-separated extra origins (e.g. Vercel URL)

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
