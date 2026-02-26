"""Fetch competitor job listings via SerpAPI Google Jobs. Returns agent-compatible dicts."""

from typing import Any

import httpx

from config import settings

DEFAULT_TIMEOUT = 20.0
MAX_ITEMS = 15


def _serpapi_request(params: dict[str, str]) -> dict[str, Any]:
    """Call SerpAPI Google Jobs and return JSON."""
    api_key = settings.serpapi_key
    if not api_key:
        raise ValueError("SERPAPI_KEY is required for jobs scraping")
    params = {**params, "api_key": api_key, "engine": "google_jobs"}
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        resp = client.get("https://serpapi.com/search", params=params)
        resp.raise_for_status()
        data = resp.json()
    if data.get("error"):
        raise RuntimeError(f"SerpAPI error: {data.get('error', 'Unknown')}")
    return data


def fetch_job_listings(
    competitor_name: str,
    *,
    location: str | None = "United States",
) -> list[dict[str, Any]]:
    """
    Fetch job listings for a competitor via SerpAPI Google Jobs.

    Args:
        competitor_name: Company name (e.g. "AppFolio", "Buildium")
        location: Optional location filter

    Returns:
        List of dicts with title, url, snippet, date (agent-compatible)
    """
    q = f"{competitor_name} jobs"
    params: dict[str, str] = {"q": q}
    if location:
        params["location"] = location

    try:
        data = _serpapi_request(params)
    except (httpx.HTTPError, ValueError, RuntimeError) as e:
        raise RuntimeError(f"Jobs scrape failed: {e}") from e

    items: list[dict[str, Any]] = []
    for job in data.get("jobs_results", [])[:MAX_ITEMS]:
        title = job.get("title")
        link = job.get("link")
        snippet = job.get("description") or job.get("snippet", "")
        date = job.get("posted_at")
        if date is None and job.get("extensions"):
            ext = job["extensions"]
            date = ext[0] if isinstance(ext, list) and ext else None
        if title or link:
            items.append({
                "title": title,
                "url": link,
                "snippet": snippet[:1000] if snippet else None,
                "date": str(date) if date else None,
            })
    return items
