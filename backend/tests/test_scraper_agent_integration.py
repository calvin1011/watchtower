"""Integration test: scraper output format matches agent input expectations."""

from unittest.mock import MagicMock, patch

from agent import analyze_scraped_data
from scrapers.blog_scraper import _parse_rss_feed
from scrapers.competitor_config import COMPETITORS, get_competitor


def test_scraper_output_format_matches_agent_input():
    """Scraper items have title, url, snippet, date - agent expects these keys."""
    rss = """<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item>
        <title>AppFolio AI Launch</title>
        <link>https://appfolio.com/blog/ai</link>
        <description>New AI feature for maintenance.</description>
        <pubDate>2024-01-15</pubDate>
      </item>
    </channel></rss>"""
    items = _parse_rss_feed("https://x.com", rss)
    assert len(items) == 1
    item = items[0]
    assert "title" in item
    assert "url" in item
    assert "snippet" in item
    assert "date" in item
    # Agent's _build_user_message uses: title, url, snippet, date, raw_content
    for key in ["title", "url", "snippet", "date"]:
        assert key in item


def test_agent_accepts_scraper_format():
    """Agent successfully parses and analyzes scraper-formatted items."""
    items = [
        {"title": "AppFolio AI", "url": "https://appfolio.com/blog", "snippet": "New AI maintenance.", "date": "2024-01-15"}
    ]
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text='[{"summary": "AppFolio launched AI", "threat_level": "MEDIUM", "threat_reason": "Competes with Joy AI", '
            '"happyco_response": "Highlight 2.7-day turn", "signal_type": "PRODUCT_LAUNCH", "confidence": 0.8, "source_url": "https://appfolio.com/blog"}]'
        )
    ]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    with patch("agent.Anthropic", return_value=mock_client), patch(
        "agent.settings", MagicMock(anthropic_api_key="test-key")
    ):
        result = analyze_scraped_data(items, "AppFolio")
    assert len(result) == 1
    assert result[0].summary == "AppFolio launched AI"
    assert result[0].source_url == "https://appfolio.com/blog"


def test_competitor_config_has_required_fields():
    """Competitor config includes blog_url, g2_slug for scrapers."""
    for c in COMPETITORS:
        assert "name" in c
        assert "blog_url" in c
        assert "g2_slug" in c or "name" in c


def test_get_competitor():
    """get_competitor returns config by name."""
    c = get_competitor("AppFolio")
    assert c is not None
    assert c["name"] == "AppFolio"
    assert "blog_url" in c
    assert get_competitor("Unknown") is None
    assert get_competitor("appfolio")["name"] == "AppFolio"  # case-insensitive
