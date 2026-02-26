"""Tests for jobs scraper. Uses mocked SerpAPI."""

from unittest.mock import MagicMock, patch

import pytest

from scrapers.jobs_scraper import fetch_job_listings


@patch("scrapers.jobs_scraper._serpapi_request")
def test_fetch_job_listings_returns_items(mock_serp):
    """fetch_job_listings returns agent-compatible items from SerpAPI."""
    mock_serp.return_value = {
        "jobs_results": [
            {
                "title": "Software Engineer",
                "link": "https://jobs.appfolio.com/1",
                "description": "Build property management software.",
                "posted_at": "2 days ago",
            },
            {
                "title": "Product Manager",
                "link": "https://jobs.appfolio.com/2",
            },
        ]
    }
    with patch("scrapers.jobs_scraper.settings", MagicMock(serpapi_key="test")):
        items = fetch_job_listings("AppFolio")
    assert len(items) == 2
    assert items[0]["title"] == "Software Engineer"
    assert items[0]["url"] == "https://jobs.appfolio.com/1"
    assert "property management" in (items[0]["snippet"] or "")
    assert items[0]["date"] == "2 days ago"
    assert items[1]["title"] == "Product Manager"


def test_fetch_job_listings_raises_without_api_key():
    """fetch_job_listings raises when SERPAPI_KEY is missing."""
    with patch("scrapers.jobs_scraper.settings", MagicMock(serpapi_key=None)):
        with pytest.raises((ValueError, RuntimeError), match="SERPAPI_KEY"):
            fetch_job_listings("AppFolio")
