"""Tests for intel service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.intel_service import get_tracked_competitors


def test_get_tracked_competitors():
    """get_tracked_competitors returns competitor names from config."""
    names = get_tracked_competitors()
    assert "AppFolio" in names
    assert "Buildium" in names
    assert "SmartRent" in names
    assert "Entrata" in names
    assert len(names) == 4
