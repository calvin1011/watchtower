"""Claude-powered competitive intelligence analysis agent."""

import json
from typing import Any

from anthropic import Anthropic
from pydantic import BaseModel

from config import settings

# HappyCo context for the agent
HAPPYCO_CONTEXT = """
You are a competitive intelligence analyst for HappyCo, the leading property operations platform.

HappyCo differentiators:
- Joy AI: AI-powered maintenance and operations
- 5.5M+ units under management
- 2.7-day average unit turn (benchmark: industry 5–7 days)
- Centralized maintenance (vs.分散 on-site)
- Plugin marketplace / open API ecosystem
- 11-point renewal gap advantage on resident satisfaction

Signal types to detect: PRODUCT_LAUNCH, PRICING_CHANGE, MARKETING_SHIFT, HIRING_SIGNAL, CUSTOMER_COMPLAINT, PARTNERSHIP.

Threat levels:
- HIGH: Direct attack on HappyCo core differentiators (centralization, turn time, AI, marketplace)
- MEDIUM: Adjacent move affecting market position
- LOW: General news, not directly threatening

Analyze competitor data and produce structured intel. Be concise. Focus on actionable insights.
"""


class IntelAnalysis(BaseModel):
    """Output schema for a single intel item from the agent."""

    summary: str
    threat_level: str  # HIGH | MEDIUM | LOW
    threat_reason: str
    happyco_response: str
    signal_type: str
    confidence: float  # 0.0–1.0
    source_url: str | None = None


def _build_user_message(items: list[dict[str, Any]], competitor: str) -> str:
    """Build the user message from raw scraped data."""
    formatted = []
    for i, item in enumerate(items, 1):
        parts = [f"Item {i}:"]
        if item.get("title"):
            parts.append(f"  Title: {item['title']}")
        if item.get("url"):
            parts.append(f"  URL: {item['url']}")
        if item.get("snippet"):
            parts.append(f"  Snippet: {item['snippet']}")
        if item.get("date"):
            parts.append(f"  Date: {item['date']}")
        if item.get("raw_content"):
            parts.append(f"  Content: {item['raw_content'][:2000]}")  # Limit length
        formatted.append("\n".join(parts))
    body = "\n\n".join(formatted)
    return f"Competitor: {competitor}\n\nAnalyze the following scraped data and return a JSON array of intel analyses.\nOne analysis per item. Use the exact keys: summary, threat_level, threat_reason, happyco_response, signal_type, confidence, source_url.\n\n{body}\n\nReturn ONLY valid JSON. No markdown or extra text."


def analyze_scraped_data(
    items: list[dict[str, Any]],
    competitor: str,
) -> list[IntelAnalysis]:
    """
    Analyze raw scraped data with Claude and return structured intel.

    Args:
        items: List of dicts with title, url, snippet, date, optionally raw_content
        competitor: Competitor name (e.g. AppFolio, Buildium)

    Returns:
        List of IntelAnalysis, one per input item
    """
    if not items:
        return []

    api_key = settings.anthropic_api_key
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is required for agent analysis")

    client = Anthropic(api_key=api_key)
    user_message = _build_user_message(items, competitor)

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system=HAPPYCO_CONTEXT,
        messages=[{"role": "user", "content": user_message}],
    )

    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    # Parse JSON from response (handle potential markdown code blocks)
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    data = json.loads(text)

    if isinstance(data, dict):
        data = [data]

    analyses = []
    for i, d in enumerate(data):
        if i < len(items) and items[i].get("url") and not d.get("source_url"):
            d = {**d, "source_url": items[i]["url"]}
        analyses.append(IntelAnalysis(**d))
    return analyses
