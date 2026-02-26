from datetime import date

import pytest
from sqlalchemy import select

from models import Digest, IntelItem


@pytest.mark.asyncio
async def test_init_db_and_session(db_session):  # noqa: ARG001
    assert db_session is not None


@pytest.mark.asyncio
async def test_insert_and_query_intel_item(db_session):
    item = IntelItem(
        competitor="AppFolio",
        signal_type="PRODUCT_LAUNCH",
        threat_level="HIGH",
        threat_reason="Test threat",
        summary="Test summary",
        happyco_response="Test response",
        confidence=0.9,
        source_url="https://example.com",
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    assert item.id is not None
    assert item.detected_at is not None
    result = await db_session.execute(select(IntelItem).where(IntelItem.competitor == "AppFolio"))
    found = result.scalar_one()
    assert found.summary == "Test summary"
    await db_session.delete(found)
    await db_session.commit()


@pytest.mark.asyncio
async def test_insert_and_query_digest(db_session):
    digest = Digest(
        week_of=date.today(),
        content={"high": [], "medium": [], "low": []},
        recipient="test@example.com",
    )
    db_session.add(digest)
    await db_session.commit()
    await db_session.refresh(digest)
    assert digest.id is not None
    assert digest.sent_at is not None
    result = await db_session.execute(select(Digest).where(Digest.recipient == "test@example.com"))
    found = result.scalar_one()
    assert found.content["high"] == []
    await db_session.delete(found)
    await db_session.commit()
