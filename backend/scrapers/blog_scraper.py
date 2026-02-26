"""Fetch competitor blog/news posts via HTTP. Returns data compatible with agent input."""

import re
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

# Rate limit: max requests per domain
DEFAULT_TIMEOUT = 15.0
MAX_ITEMS = 20


def _parse_rss_feed(url: str, html: str) -> list[dict[str, Any]]:
    """Parse RSS/Atom XML feed. Returns list of {title, url, snippet, date}."""
    items: list[dict[str, Any]] = []
    try:
        root = ET.fromstring(html)
    except ET.ParseError:
        return items

    # RSS 2.0: channel/item - iter over all, filter for item tag (handles namespaces)
    for elem in root.iter():
        tag = elem.tag.split("}")[-1] if isinstance(elem.tag, str) and "}" in elem.tag else elem.tag
        if tag != "item":
            continue
        item = elem
        entry: dict[str, Any] = {}
        for child in item:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "title" and child.text:
                entry["title"] = child.text.strip()
            elif tag == "link":
                href = child.text or child.get("href", "")
                if href:
                    entry["url"] = urljoin(url, href)
            elif tag == "description" and child.text:
                text = child.text.strip()
                entry["snippet"] = text[:500] if len(text) > 500 else text
            elif tag == "pubDate" and child.text:
                entry["date"] = child.text.strip()
        if entry.get("title") or entry.get("url"):
            items.append(entry)

    # Atom: feed/entry
    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        e: dict[str, Any] = {}
        title_el = entry.find("{http://www.w3.org/2005/Atom}title")
        if title_el is not None and title_el.text:
            e["title"] = title_el.text.strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link[@href]")
        if link_el is not None:
            e["url"] = urljoin(url, link_el.get("href", ""))
        summary_el = entry.find("{http://www.w3.org/2005/Atom}summary")
        if summary_el is not None and summary_el.text:
            text = summary_el.text.strip()
            e["snippet"] = text[:500] if len(text) > 500 else text
        updated_el = entry.find("{http://www.w3.org/2005/Atom}updated")
        if updated_el is not None and updated_el.text:
            e["date"] = updated_el.text.strip()
        if e.get("title") or e.get("url"):
            items.append(e)

    return items[:MAX_ITEMS]


def _parse_html_articles(html: str, base_url: str) -> list[dict[str, Any]]:
    """Fallback: extract article links from HTML using common patterns."""
    items: list[dict[str, Any]] = []
    # Match links with blog/news/article/post in path
    pattern = r'<a[^>]+href=["\']([^"\']*(?:/blog/|/news/|/article/|/post/)[^"\']*)["\'][^>]*>([^<]*)</a>'
    seen_urls: set[str] = set()
    for m in re.finditer(pattern, html, re.IGNORECASE):
        href, title = m.group(1), m.group(2).strip()
        full_url = urljoin(base_url, href)
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)
        parsed = urlparse(full_url)
        if parsed.netloc and parsed.path and len(parsed.path) > 5:
            items.append({
                "title": title[:200] if title else None,
                "url": full_url,
                "snippet": None,
                "date": None,
            })
        if len(items) >= MAX_ITEMS:
            break
    return items


def fetch_blog_posts(
    blog_url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> list[dict[str, Any]]:
    """
    Fetch blog posts from a competitor blog URL.

    Tries RSS/Atom feed first (common paths: /feed, /rss, /blog/feed).
    Falls back to HTML link extraction.

    Returns:
        List of dicts with title, url, snippet, date (agent-compatible)
    """
    items: list[dict[str, Any]] = []
    feed_paths = ["/feed", "/rss", "/blog/feed", "/feed/", "/rss/", ""]

    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        for path in feed_paths:
            url = urljoin(blog_url, path) if path else blog_url
            try:
                resp = client.get(url)
                resp.raise_for_status()
                ct = resp.headers.get("content-type", "").lower()
                if "xml" in ct or "rss" in ct or "atom" in ct:
                    items = _parse_rss_feed(url, resp.text)
                    if items:
                        return items
            except Exception:
                continue

        # Fallback: fetch main blog page and extract links
        try:
            resp = client.get(blog_url)
            resp.raise_for_status()
            items = _parse_html_articles(resp.text, blog_url)
        except Exception:
            pass

    return items
