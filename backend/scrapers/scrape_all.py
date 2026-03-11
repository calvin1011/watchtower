"""Convenience: scrape all sources for a competitor. Used by Phase 5 intel pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from scrapers.blog_scraper import fetch_blog_posts
from scrapers.competitor_config import get_competitor
from scrapers.jobs_scraper import fetch_job_listings
from scrapers.review_scraper import fetch_reviews

if TYPE_CHECKING:
    from models import Competitor


def scrape_competitor(competitor: Competitor | str) -> list[dict[str, Any]]:
    """
    Scrape all configured sources for a competitor.

    Accepts a Competitor model (uses blog_url, g2_slug, capterra_slug, name) or
    a string name (uses competitor_config for backward compatibility).

    Runs: blog, reviews (G2/Capterra), jobs. Skips website scraper by default
    (Playwright is heavy; can be enabled optionally).

    Returns:
        Combined list of agent-compatible dicts (title, url, snippet, date, raw_content)
    """
    if isinstance(competitor, str):
        config = get_competitor(competitor)
        name = competitor
        blog_url = (config or {}).get("blog_url")
        g2_slug = (config or {}).get("g2_slug")
        capterra_slug = (config or {}).get("capterra_slug")
    else:
        config = None
        name = competitor.name
        blog_url = competitor.blog_url
        g2_slug = competitor.g2_slug
        capterra_slug = competitor.capterra_slug

    items: list[dict[str, Any]] = []

    if blog_url:
        try:
            items.extend(fetch_blog_posts(blog_url))
        except Exception:
            pass

    try:
        items.extend(
            fetch_reviews(
                name,
                g2_slug=g2_slug,
                capterra_slug=capterra_slug,
            )
        )
    except Exception:
        pass

    try:
        items.extend(fetch_job_listings(name))
    except Exception:
        pass

    return items
