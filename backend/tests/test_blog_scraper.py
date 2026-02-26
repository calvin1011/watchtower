"""Tests for blog scraper. Uses mocked HTTP to avoid network calls."""

from unittest.mock import MagicMock, patch

import pytest

from scrapers.blog_scraper import (
    _parse_html_articles,
    _parse_rss_feed,
    fetch_blog_posts,
)


def test_parse_rss_feed():
    """Parse RSS XML into agent-compatible items."""
    rss = """<?xml version="1.0"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>AppFolio Launches AI Feature</title>
          <link>https://appfolio.com/blog/ai-feature</link>
          <description>New AI maintenance feature announced.</description>
          <pubDate>Mon, 15 Jan 2024 12:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """
    items = _parse_rss_feed("https://example.com/feed", rss)
    assert len(items) == 1
    assert items[0]["title"] == "AppFolio Launches AI Feature"
    assert items[0]["url"] == "https://appfolio.com/blog/ai-feature"
    assert "AI maintenance" in items[0]["snippet"]
    assert "15 Jan 2024" in items[0]["date"]


def test_parse_rss_empty_returns_empty():
    """Invalid or empty XML returns empty list."""
    assert _parse_rss_feed("https://x.com", "") == []
    assert _parse_rss_feed("https://x.com", "<invalid") == []


def test_parse_html_articles():
    """Extract article links from HTML."""
    html = """
    <a href="/blog/post-1">First Post</a>
    <a href="https://example.com/blog/post-2">Second Post</a>
    """
    items = _parse_html_articles(html, "https://example.com")
    assert len(items) >= 2
    urls = [i["url"] for i in items]
    assert any("post-1" in u for u in urls)
    assert any("post-2" in u for u in urls)


@patch("scrapers.blog_scraper.httpx.Client")
def test_fetch_blog_posts_uses_rss(MockClient):
    """fetch_blog_posts returns items from RSS when available."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"content-type": "application/rss+xml"}
    mock_resp.text = """<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item><title>T1</title><link>https://x.com/1</link><description>D1</description></item>
    </channel></rss>"""
    mock_resp.raise_for_status = MagicMock()

    mock_instance = MagicMock()
    mock_instance.get.return_value = mock_resp
    mock_instance.__enter__ = MagicMock(return_value=mock_instance)
    mock_instance.__exit__ = MagicMock(return_value=False)
    MockClient.return_value = mock_instance

    items = fetch_blog_posts("https://example.com/blog")
    assert len(items) == 1
    assert items[0]["title"] == "T1"
    assert items[0]["url"] == "https://x.com/1"


@patch("scrapers.blog_scraper.httpx.Client")
def test_fetch_blog_posts_handles_http_error(MockClient):
    """fetch_blog_posts returns empty list on HTTP errors."""
    mock_instance = MagicMock()
    mock_instance.get.side_effect = Exception("Connection error")
    mock_instance.__enter__ = MagicMock(return_value=mock_instance)
    mock_instance.__exit__ = MagicMock(return_value=False)
    MockClient.return_value = mock_instance

    items = fetch_blog_posts("https://example.com/blog")
    assert items == []
