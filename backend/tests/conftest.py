import os

import pytest
from dotenv import load_dotenv

from database import init_db

load_dotenv()

requires_db = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL not set; integration tests require database",
)


@pytest.fixture
def database_url():
    return os.getenv("DATABASE_URL")


@pytest.fixture
async def db_session(database_url):
    if not database_url:
        pytest.skip("DATABASE_URL not set")
    init_db(database_url)
    from database import _session_factory
    async with _session_factory() as session:
        yield session
