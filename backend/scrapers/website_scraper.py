"""Fetch competitor website content via Playwright. Returns agent-compatible dicts with raw_content."""

from typing import Any

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None  # type: ignore

MAX_RAW_CONTENT = 8000


def fetch_website_content(
    website_url: str,
    *,
    title: str | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch main page content from a competitor website using Playwright.

    Use for dynamic/JS-rendered pages. Returns a single-item list with raw_content
    for the agent to analyze (e.g. product messaging, feature claims).

    Args:
        website_url: Full URL (e.g. https://www.appfolio.com)
        title: Optional title for the item (default: homepage)

    Returns:
        List of one dict with title, url, snippet, date, raw_content
    """
    if sync_playwright is None:
        raise ImportError("playwright is required for website_scraper. Install: pip install playwright && playwright install chromium")

    item: dict[str, Any] = {
        "title": title or "Homepage",
        "url": website_url.rstrip("/"),
        "snippet": None,
        "date": None,
        "raw_content": None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(website_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)  # Allow JS to render
            text = page.evaluate("""() => {
                const body = document.body;
                if (!body) return '';
                const walk = (node) => {
                    let out = '';
                    for (const n of node.childNodes) {
                        if (n.nodeType === 3) out += n.textContent || '';
                        else if (n.nodeType === 1) {
                            const tag = (n.tagName || '').toLowerCase();
                            if (tag === 'script' || tag === 'style' || tag === 'nav') continue;
                            out += walk(n) + ' ';
                        }
                    }
                    return out;
                };
                return walk(body).replace(/\\s+/g, ' ').trim();
            }""")
            if text:
                item["raw_content"] = text[:MAX_RAW_CONTENT]
                item["snippet"] = text[:300] + "..." if len(text) > 300 else text
        finally:
            browser.close()

    return [item]
