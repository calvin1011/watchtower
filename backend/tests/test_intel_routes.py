"""Tests for intel API routes."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from main import app


# Avoid "Database not initialized" when testing without DATABASE_URL
@pytest.fixture
def mock_db_session():
    """Provide a fake session so routes don't require real DB."""

    async def fake_get_session():
        yield MagicMock()

    return fake_get_session


@pytest.fixture
def client_with_db(mock_db_session):
    """Test client with overridden get_session."""
    from database import get_session

    app.dependency_overrides[get_session] = mock_db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_list_intel_empty(client_with_db):
    """GET /intel returns empty list when no items."""
    with patch("routes.intel.get_intel_items", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        resp = client_with_db.get("/intel")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["count"] == 0


def test_list_intel_returns_items(client_with_db):
    """GET /intel returns serialized intel items."""
    fake_item = MagicMock()
    fake_item.id = uuid4()
    fake_item.competitor = "AppFolio"
    fake_item.signal_type = "PRODUCT_LAUNCH"
    fake_item.threat_level = "MEDIUM"
    fake_item.threat_reason = "Competes with Joy AI"
    fake_item.summary = "AppFolio launched AI feature"
    fake_item.happyco_response = "Highlight scale"
    fake_item.confidence = 0.8
    fake_item.source_url = "https://example.com"
    fake_item.detected_at = datetime.now(UTC)
    fake_item.created_at = datetime.now(UTC)

    with patch("routes.intel.get_intel_items", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [fake_item]
        resp = client_with_db.get("/intel")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["items"][0]["competitor"] == "AppFolio"
    assert data["items"][0]["signal_type"] == "PRODUCT_LAUNCH"
    assert data["items"][0]["summary"] == "AppFolio launched AI feature"


def test_list_intel_by_competitor(client_with_db):
    """GET /intel/{competitor} filters by competitor."""
    with patch("routes.intel.get_intel_items", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        resp = client_with_db.get("/intel/AppFolio")
    assert resp.status_code == 200
    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args[1]
    assert call_kwargs["competitor"] == "AppFolio"


def test_list_intel_by_signal(client_with_db):
    """GET /intel/signals/{type} filters by signal type."""
    with patch("routes.intel.get_intel_items", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        resp = client_with_db.get("/intel/signals/PRODUCT_LAUNCH")
    assert resp.status_code == 200
    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args[1]
    assert call_kwargs["signal_type"] == "PRODUCT_LAUNCH"


def test_get_intel_item_not_found(client_with_db):
    """GET /intel/item/{id} returns 404 when item missing."""
    with patch("routes.intel.get_intel_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        resp = client_with_db.get(f"/intel/item/{uuid4()}")
    assert resp.status_code == 404


def test_get_intel_item_found(client_with_db):
    """GET /intel/item/{id} returns item when found."""
    item_id = uuid4()
    fake_item = MagicMock()
    fake_item.id = item_id
    fake_item.competitor = "Buildium"
    fake_item.signal_type = "HIRING_SIGNAL"
    fake_item.threat_level = "LOW"
    fake_item.threat_reason = "Expanding team"
    fake_item.summary = "Buildium hiring"
    fake_item.happyco_response = "Monitor"
    fake_item.confidence = 0.6
    fake_item.source_url = None
    fake_item.detected_at = datetime.now(UTC)
    fake_item.created_at = datetime.now(UTC)

    with patch("routes.intel.get_intel_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = fake_item
        resp = client_with_db.get(f"/intel/item/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["competitor"] == "Buildium"


def test_run_pipeline_unknown_competitor(client_with_db):
    """POST /intel/run?competitor=Unknown returns 400."""
    with patch("routes.intel.get_tracked_competitors", return_value=["AppFolio", "Buildium"]):
        resp = client_with_db.post("/intel/run?competitor=Unknown")
    assert resp.status_code == 400
    assert "Unknown competitor" in resp.json()["detail"]


def test_search_intel(client_with_db):
    """GET /intel/search?q=... returns semantically similar items."""
    with patch("routes.intel.get_intel_semantic_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = []
        resp = client_with_db.get("/intel/search?q=AI+maintenance+feature")
    assert resp.status_code == 200
    mock_search.assert_called_once()
    call_args = mock_search.call_args
    assert call_args[0][1] == "AI maintenance feature"  # query
    assert call_args[1]["limit"] == 20


def test_run_pipeline_success(client_with_db):
    """POST /intel/run creates intel and returns count."""
    with (
        patch("routes.intel.get_tracked_competitors", return_value=["AppFolio"]),
        patch("routes.intel.run_pipeline", new_callable=AsyncMock) as mock_run,
    ):
        mock_run.return_value = [MagicMock()]  # one created item
        resp = client_with_db.post("/intel/run?competitor=AppFolio")
    assert resp.status_code == 200
    data = resp.json()
    assert data["created"] == 1
    assert "AppFolio" in data["competitors_run"]
