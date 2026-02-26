"""Convenience: scrape all sources for a competitor. Used by Phase 5 intel pipeline."""

from typing import Any

from scrapers.blog_scraper import fetch_blog_posts
from scrapers.competitor_config import get_competitor
from scrapers.jobs_scraper import fetch_job_listings
from scrapers.review_scraper import fetch_reviews


def scrape_competitor(competitor_name: str) -> list[dict[str, Any]]:
    """
    Scrape all configured sources for a competitor.

    Runs: blog, reviews (G2/Capterra), jobs. Skips website scraper by default
    (Playwright is heavy; can be enabled optionally).

    Returns:
        Combined list of agent-compatible dicts (title, url, snippet, date, raw_content)
    """
    config = get_competitor(competitor_name)
    items: list[dict[str, Any]] = []

    blog_url = (config or {}).get("blog_url")
    if blog_url:
        try:
            items.extend(fetch_blog_posts(blog_url))
        except Exception:
            pass

    try:
        cfg = config or {}
        items.extend(
            fetch_reviews(
                competitor_name,
                g2_slug=cfg.get("g2_slug"),
                capterra_slug=cfg.get("capterra_slug"),
            )
        )
    except Exception:
        pass

    try:
        items.extend(fetch_job_listings(competitor_name))
    except Exception:
        pass

    return items
