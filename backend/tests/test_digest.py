"""Tests for digest module and routes."""

from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from digest import _build_html_email, _group_by_threat, _item_to_dict, build_digest
from main import app

# --- Unit tests for digest logic ---


def test_item_to_dict():
    """_item_to_dict serializes IntelItem to dict."""
    item = MagicMock()
    item.id = uuid4()
    item.competitor = "AppFolio"
    item.signal_type = "PRODUCT_LAUNCH"
    item.threat_level = "HIGH"
    item.threat_reason = "AI feature"
    item.summary = "Launched AI"
    item.happyco_response = "Highlight scale"
    item.source_url = "https://example.com"
    item.detected_at = datetime(2025, 2, 24, 10, 0, 0, tzinfo=UTC)

    d = _item_to_dict(item)
    assert d["competitor"] == "AppFolio"
    assert d["signal_type"] == "PRODUCT_LAUNCH"
    assert d["threat_level"] == "HIGH"
    assert d["summary"] == "Launched AI"
    assert d["happyco_response"] == "Highlight scale"
    assert "2025-02-24" in d["detected_at"]


def test_group_by_threat():
    """_group_by_threat groups items by HIGH, MEDIUM, LOW."""
    items = [
        MagicMock(threat_level="HIGH", summary="a"),
        MagicMock(threat_level="LOW", summary="b"),
        MagicMock(threat_level="MEDIUM", summary="c"),
        MagicMock(threat_level="HIGH", summary="d"),
    ]
    grouped = _group_by_threat(items)
    assert len(grouped["HIGH"]) == 2
    assert len(grouped["MEDIUM"]) == 1
    assert len(grouped["LOW"]) == 1
    assert grouped["HIGH"][0].summary == "a"


def test_build_html_email_empty():
    """_build_html_email handles empty grouped content."""
    content = {"grouped": {}, "week_of": "2025-02-24"}
    html = _build_html_email(content, date(2025, 2, 24))
    assert "No new intel this week" in html
    assert "February 24, 2025" in html


def test_build_html_email_with_items():
    """_build_html_email includes happyco_response per item."""
    content = {
        "grouped": {
            "HIGH": [
                {
                    "competitor": "AppFolio",
                    "summary": "AI launch",
                    "threat_reason": "Competes",
                    "happyco_response": "Highlight scale",
                    "source_url": "https://example.com",
                }
            ]
        },
    }
    html = _build_html_email(content, date(2025, 2, 24))
    assert "AppFolio" in html
    assert "AI launch" in html
    assert "HappyCo response" in html
    assert "Highlight scale" in html


# --- Route tests ---


@pytest.fixture
def mock_db_session():
    async def fake_get_session():
        yield MagicMock()

    return fake_get_session


@pytest.fixture
def client_with_db(mock_db_session):
    from database import get_session

    app.dependency_overrides[get_session] = mock_db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_digest_history_empty(client_with_db):
    """GET /digest/history returns empty list when no digests."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session = MagicMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    async def fake_session():
        yield mock_session

    from database import get_session

    app.dependency_overrides[get_session] = fake_session
    try:
        resp = client_with_db.get("/digest/history")
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["digests"] == []
    assert data["count"] == 0


def test_digest_send_no_resend_key(client_with_db):
    """POST /digest/send returns 503 when RESEND_API_KEY not set."""
    with patch("routes.digest.settings") as mock_settings:
        mock_settings.resend_api_key = None
        resp = client_with_db.post("/digest/send")
    assert resp.status_code == 503
    assert "RESEND_API_KEY" in resp.json()["detail"]


def test_digest_send_success(client_with_db):
    """POST /digest/send succeeds and returns digest when Resend sends."""
    fake_digest = MagicMock()
    fake_digest.id = uuid4()
    fake_digest.week_of = date(2025, 2, 24)
    fake_digest.content = {"grouped": {}, "week_of": "2025-02-24"}
    fake_digest.sent_at = datetime.now(UTC)
    fake_digest.recipient = "test@example.com"

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def fake_session():
        yield mock_session

    with (
        patch("routes.digest.settings") as mock_settings,
        patch("routes.digest.create_and_send_digest", new_callable=AsyncMock) as mock_send,
    ):
        mock_settings.resend_api_key = "re_test123"
        mock_send.return_value = fake_digest

        from database import get_session
        app.dependency_overrides[get_session] = fake_session

        resp = client_with_db.post("/digest/send")
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Digest sent"
    assert "digest" in data
    assert data["digest"]["recipient"] == "test@example.com"


@pytest.mark.asyncio
async def test_build_digest_async():
    """build_digest returns content and week_of."""
    mock_session = AsyncMock()

    with patch("digest.get_intel_items", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        content, week_of = await build_digest(mock_session, since_days=7)

    assert "grouped" in content
    assert "week_of" in content
    assert "total_items" in content
    assert content["total_items"] == 0
    assert isinstance(week_of, date)
