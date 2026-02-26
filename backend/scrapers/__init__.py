"""Scrapers for competitor data collection.

Each scraper returns a list of dicts compatible with agent.analyze_scraped_data():
- title: str | None
- url: str | None
- snippet: str | None
- date: str | None
- raw_content: str | None (optional, for blog/website scrapers)
"""

from scrapers.blog_scraper import fetch_blog_posts
from scrapers.competitor_config import COMPETITORS, get_competitor
from scrapers.jobs_scraper import fetch_job_listings
from scrapers.review_scraper import fetch_reviews
from scrapers.scrape_all import scrape_competitor
from scrapers.website_scraper import fetch_website_content

__all__ = [
    "COMPETITORS",
    "get_competitor",
    "scrape_competitor",
    "fetch_blog_posts",
    "fetch_reviews",
    "fetch_job_listings",
    "fetch_website_content",
]
