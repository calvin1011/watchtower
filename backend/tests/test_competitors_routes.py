"""Minimal tests for competitors API: list, create, patch, soft-delete."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from main import app


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


def test_list_competitors_empty(client_with_db):
    """GET /competitors returns empty list when no competitors."""
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    async def session_factory():
        yield mock_session

    from database import get_session
    app.dependency_overrides[get_session] = session_factory
    try:
        resp = client_with_db.get("/competitors")
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["competitors"] == []
    assert data["count"] == 0


def test_list_competitors_with_data(client_with_db):
    """GET /competitors returns serialized competitors."""
    mock_comp = MagicMock()
    mock_comp.id = uuid4()
    mock_comp.name = "AppFolio"
    mock_comp.slug = "appfolio"
    mock_comp.website_url = "https://www.appfolio.com"
    mock_comp.blog_url = "https://www.appfolio.com/blog"
    mock_comp.g2_slug = "appfolio"
    mock_comp.capterra_slug = "appfolio-property-management"
    mock_comp.is_active = True
    mock_comp.created_at = datetime.now(UTC)
    mock_comp.updated_at = datetime.now(UTC)

    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_comp]
    mock_session.execute = AsyncMock(return_value=mock_result)

    async def session_factory():
        yield mock_session

    from database import get_session
    app.dependency_overrides[get_session] = session_factory
    try:
        resp = client_with_db.get("/competitors")
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["competitors"][0]["name"] == "AppFolio"
    assert data["competitors"][0]["slug"] == "appfolio"
    assert data["competitors"][0]["is_active"] is True


def test_create_competitor(client_with_db):
    """POST /competitors creates a competitor and returns 201."""
    mock_session = MagicMock()
    mock_existing = MagicMock()
    mock_existing.scalar_one_or_none.return_value = None  # no slug conflict
    mock_session.execute = AsyncMock(return_value=mock_existing)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def session_factory():
        yield mock_session

    from database import get_session
    app.dependency_overrides[get_session] = session_factory
    try:
        resp = client_with_db.post(
            "/competitors",
            json={
                "name": "NewCo",
                "blog_url": "https://newco.com/blog",
                "g2_slug": "newco",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "NewCo"
    assert data["slug"] == "newco"
    assert data["blog_url"] == "https://newco.com/blog"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_create_competitor_slug_conflict(client_with_db):
    """POST /competitors returns 409 when slug already exists."""
    mock_existing_comp = MagicMock()
    mock_session = MagicMock()
    mock_existing = MagicMock()
    mock_existing.scalar_one_or_none.return_value = mock_existing_comp  # slug exists
    mock_session.execute = AsyncMock(return_value=mock_existing)

    async def session_factory():
        yield mock_session

    from database import get_session
    app.dependency_overrides[get_session] = session_factory
    try:
        resp = client_with_db.post(
            "/competitors",
            json={"name": "AppFolio"},
        )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


def test_patch_competitor(client_with_db):
    """PATCH /competitors/{id} updates a competitor."""
    comp_id = uuid4()
    mock_comp = MagicMock()
    mock_comp.id = comp_id
    mock_comp.name = "AppFolio"
    mock_comp.slug = "appfolio"
    mock_comp.website_url = None
    mock_comp.blog_url = None
    mock_comp.g2_slug = None
    mock_comp.capterra_slug = None
    mock_comp.is_active = True
    mock_comp.created_at = datetime.now(UTC)
    mock_comp.updated_at = datetime.now(UTC)

    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    with patch("routes.competitors._get_competitor_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_comp
        async def session_factory():
            yield mock_session
        from database import get_session
        app.dependency_overrides[get_session] = session_factory
        try:
            resp = client_with_db.patch(
                f"/competitors/{comp_id}",
                json={"blog_url": "https://appfolio.com/new-blog"},
            )
        finally:
            app.dependency_overrides.clear()

    assert resp.status_code == 200
    assert mock_comp.blog_url == "https://appfolio.com/new-blog"
    mock_session.commit.assert_called_once()


def test_patch_competitor_not_found(client_with_db):
    """PATCH /competitors/{id} returns 404 when competitor not found."""
    with patch("routes.competitors._get_competitor_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        resp = client_with_db.patch(
            f"/competitors/{uuid4()}",
            json={"name": "Other"},
        )
    assert resp.status_code == 404


def test_delete_competitor_soft_delete(client_with_db):
    """DELETE /competitors/{id} soft-deletes (sets is_active=False) and returns 204."""
    comp_id = uuid4()
    mock_comp = MagicMock()
    mock_comp.id = comp_id
    mock_comp.name = "AppFolio"
    mock_comp.is_active = True

    mock_session = MagicMock()
    mock_session.commit = AsyncMock()

    with patch("routes.competitors._get_competitor_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_comp
        async def session_factory():
            yield mock_session
        from database import get_session
        app.dependency_overrides[get_session] = session_factory
        try:
            resp = client_with_db.delete(f"/competitors/{comp_id}")
        finally:
            app.dependency_overrides.clear()

    assert resp.status_code == 204
    assert mock_comp.is_active is False
    mock_session.commit.assert_called_once()


def test_delete_competitor_not_found(client_with_db):
    """DELETE /competitors/{id} returns 404 when competitor not found."""
    with patch("routes.competitors._get_competitor_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        resp = client_with_db.delete(f"/competitors/{uuid4()}")
    assert resp.status_code == 404
