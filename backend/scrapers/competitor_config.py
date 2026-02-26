"""Competitor source configuration. Shared by scrapers and Phase 5 intel pipeline."""

from typing import TypedDict


class CompetitorSource(TypedDict, total=False):
    """Config for a single competitor's data sources."""

    name: str
    blog_url: str
    website_url: str
    g2_slug: str
    capterra_slug: str


# Competitors tracked by Watchtower (per ARCHITECTURE.md and README)
COMPETITORS: list[CompetitorSource] = [
    {
        "name": "AppFolio",
        "blog_url": "https://www.appfolio.com/blog",
        "website_url": "https://www.appfolio.com",
        "g2_slug": "appfolio",
        "capterra_slug": "appfolio-property-management",
    },
    {
        "name": "Buildium",
        "blog_url": "https://www.buildium.com/blog",
        "website_url": "https://www.buildium.com",
        "g2_slug": "buildium",
        "capterra_slug": "buildium",
    },
    {
        "name": "SmartRent",
        "blog_url": "https://www.smartrent.com/blog",
        "website_url": "https://www.smartrent.com",
        "g2_slug": "smartrent",
        "capterra_slug": "smartrent",
    },
    {
        "name": "Entrata",
        "blog_url": "https://www.entrata.com/blog",
        "website_url": "https://www.entrata.com",
        "g2_slug": "entrata",
        "capterra_slug": "entrata",
    },
]


def get_competitor(name: str) -> CompetitorSource | None:
    """Return config for a competitor by name, case-insensitive."""
    name_lower = name.lower().strip()
    for c in COMPETITORS:
        if c.get("name", "").lower() == name_lower:
            return c
    return None
