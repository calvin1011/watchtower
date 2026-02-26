"""Tests for review scraper. Uses mocked SerpAPI."""

from unittest.mock import MagicMock, patch

import pytest

from scrapers.review_scraper import _parse_google_organic, fetch_reviews


def test_parse_google_organic():
    """Parse SerpAPI organic results into agent format."""
    data = {
        "organic_results": [
            {
                "title": "AppFolio Reviews - G2",
                "link": "https://g2.com/products/appfolio/reviews",
                "snippet": "Users rate AppFolio 4.5 stars...",
            },
        ]
    }
    items = _parse_google_organic(data)
    assert len(items) == 1
    assert items[0]["title"] == "AppFolio Reviews - G2"
    assert items[0]["url"] == "https://g2.com/products/appfolio/reviews"
    assert "4.5 stars" in items[0]["snippet"]


@patch("scrapers.review_scraper._serpapi_request")
def test_fetch_reviews_returns_items(mock_serp):
    """fetch_reviews returns combined G2 and Capterra results."""
    mock_serp.return_value = {
        "organic_results": [
            {"title": "G2 Review", "link": "https://g2.com/1", "snippet": "S1"},
        ]
    }
    with patch("scrapers.review_scraper.settings", MagicMock(serpapi_key="test")):
        items = fetch_reviews("AppFolio")
    assert len(items) >= 1
    assert items[0]["title"] == "G2 Review"


def test_fetch_reviews_raises_without_api_key():
    """fetch_reviews raises when SERPAPI_KEY is missing."""
    with patch("scrapers.review_scraper.settings", MagicMock(serpapi_key=None)):
        with pytest.raises(ValueError, match="SERPAPI_KEY is required"):
            fetch_reviews("AppFolio")
