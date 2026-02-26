"""Intel pipeline: scrape -> analyze -> store."""

import asyncio
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent import analyze_scraped_data
from embeddings import get_embedding
from models import IntelItem
from scrapers.competitor_config import COMPETITORS
from scrapers.scrape_all import scrape_competitor


async def run_pipeline(
    competitor: str,
    session: AsyncSession,
) -> list[IntelItem]:
    """
    Scrape competitor data, analyze with Claude, and persist to DB.

    Returns the created IntelItem records.
    """
    # 1. Scrape (sync, run in thread pool)
    items = await asyncio.to_thread(scrape_competitor, competitor)
    if not items:
        return []

    # 2. Analyze (sync, run in thread pool)
    analyses = await asyncio.to_thread(analyze_scraped_data, items, competitor)
    if not analyses:
        return []

    # 3. Map and insert
    created: list[IntelItem] = []
    for i, analysis in enumerate(analyses):
        raw_item = items[i] if i < len(items) else {}
        raw_content = raw_item.get("raw_content") or raw_item.get("snippet")
        source_url = analysis.source_url or raw_item.get("url")

        intel = IntelItem(
            competitor=competitor,
            signal_type=analysis.signal_type,
            threat_level=analysis.threat_level,
            threat_reason=analysis.threat_reason,
            summary=analysis.summary,
            happyco_response=analysis.happyco_response,
            confidence=analysis.confidence,
            source_url=source_url,
            raw_content=raw_content,
        )
        # Generate embedding for semantic search (sync, run in thread pool)
        embed_text = f"{analysis.summary} {analysis.threat_reason}".strip()
        if embed_text:
            embedding = await asyncio.to_thread(get_embedding, embed_text)
            if embedding:
                intel.embedding = embedding
        session.add(intel)
        created.append(intel)

    await session.commit()
    for item in created:
        await session.refresh(item)
    return created


async def get_intel_items(
    session: AsyncSession,
    *,
    competitor: str | None = None,
    signal_type: str | None = None,
    limit: int = 100,
) -> list[IntelItem]:
    """Query intel items with optional filters."""
    stmt = select(IntelItem).order_by(IntelItem.detected_at.desc()).limit(limit)
    if competitor:
        stmt = stmt.where(IntelItem.competitor == competitor)
    if signal_type:
        stmt = stmt.where(IntelItem.signal_type == signal_type)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_intel_by_id(session: AsyncSession, item_id: UUID) -> IntelItem | None:
    """Fetch a single intel item by ID."""
    result = await session.execute(select(IntelItem).where(IntelItem.id == item_id))
    return result.scalars().first()


def get_tracked_competitors() -> list[str]:
    """Return list of competitor names we track."""
    return [c["name"] for c in COMPETITORS if c.get("name")]


async def get_intel_semantic_search(
    session: AsyncSession,
    query: str,
    *,
    limit: int = 20,
) -> list[IntelItem]:
    """
    Semantic search: find intel items most similar to the query text.

    Returns items ordered by cosine similarity (closest first).
    Returns empty list if OpenAI key missing or no embeddings exist.
    """
    embedding = await asyncio.to_thread(get_embedding, query)
    if not embedding:
        return []

    # pgvector cosine_distance: lower = more similar
    stmt = (
        select(IntelItem)
        .where(IntelItem.embedding.isnot(None))
        .order_by(IntelItem.embedding.cosine_distance(embedding))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
