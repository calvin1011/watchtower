"""Fetch competitor reviews from G2 and Capterra via SerpAPI. Returns agent-compatible dicts."""

from typing import Any

import httpx

from config import settings

DEFAULT_TIMEOUT = 20.0
MAX_ITEMS_PER_SOURCE = 15


def _serpapi_request(params: dict[str, str]) -> dict[str, Any]:
    """Call SerpAPI and return JSON. Handles rate limits and errors."""
    api_key = settings.serpapi_key
    if not api_key:
        raise ValueError("SERPAPI_KEY is required for review scraping")
    params = {**params, "api_key": api_key}
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        resp = client.get("https://serpapi.com/search", params=params)
        resp.raise_for_status()
        data = resp.json()
    if data.get("error"):
        raise RuntimeError(f"SerpAPI error: {data.get('error', 'Unknown')}")
    return data


def _parse_google_organic(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract organic results into agent-compatible format."""
    items: list[dict[str, Any]] = []
    for r in data.get("organic_results", [])[:MAX_ITEMS_PER_SOURCE]:
        title = r.get("title")
        link = r.get("link")
        snippet = r.get("snippet") or r.get("description", "")
        date = r.get("date")
        if title or link:
            items.append({
                "title": title,
                "url": link,
                "snippet": snippet,
                "date": date,
            })
    return items


def fetch_reviews(
    competitor_name: str,
    g2_slug: str | None = None,
    capterra_slug: str | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch reviews for a competitor from G2 and Capterra via Google Search (SerpAPI).
    Raises ValueError if SERPAPI_KEY is missing.

    Args:
        competitor_name: Display name (e.g. "AppFolio")
        g2_slug: G2 product slug (e.g. "appfolio")
        capterra_slug: Capterra product slug (e.g. "appfolio-property-management")

    Returns:
        List of dicts with title, url, snippet, date (agent-compatible)
    """
    items: list[dict[str, Any]] = []
    g2_slug = g2_slug or competitor_name.lower().replace(" ", "-")
    capterra_slug = capterra_slug or g2_slug

    # G2 reviews: site:g2.com "Competitor" reviews
    try:
        g2_data = _serpapi_request({
            "engine": "google",
            "q": f'site:g2.com "{competitor_name}" reviews',
            "num": 10,
        })
        items.extend(_parse_google_organic(g2_data))
    except (httpx.HTTPError, RuntimeError):
        pass
    # ValueError (missing API key) propagates

    # Capterra reviews: site:capterra.com "Competitor" reviews
    try:
        cap_data = _serpapi_request({
            "engine": "google",
            "q": f'site:capterra.com "{competitor_name}" reviews',
            "num": 10,
        })
        cap_items = _parse_google_organic(cap_data)
        # Deduplicate by URL
        seen = {i["url"] for i in items if i.get("url")}
        for c in cap_items:
            if c.get("url") and c["url"] not in seen:
                seen.add(c["url"])
                items.append(c)
            if len(items) >= MAX_ITEMS_PER_SOURCE * 2:
                break
    except (httpx.HTTPError, RuntimeError):
        pass

    return items[:MAX_ITEMS_PER_SOURCE * 2]
