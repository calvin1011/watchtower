"""Tests for intel service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.intel_service import get_tracked_competitors_from_db


@pytest.mark.asyncio
async def test_get_tracked_competitors_from_db_returns_active_competitors():
    """get_tracked_competitors_from_db returns list of Competitor models from DB."""
    mock_comp1 = MagicMock()
    mock_comp1.name = "AppFolio"
    mock_comp1.slug = "appfolio"
    mock_comp2 = MagicMock()
    mock_comp2.name = "Buildium"
    mock_comp2.slug = "buildium"

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_comp1, mock_comp2]

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    competitors = await get_tracked_competitors_from_db(mock_session)
    assert len(competitors) == 2
    assert competitors[0].name == "AppFolio"
    assert competitors[0].slug == "appfolio"
    assert competitors[1].name == "Buildium"
    assert competitors[1].slug == "buildium"
    mock_session.execute.assert_called_once()
