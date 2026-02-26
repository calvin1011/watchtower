"""Intel API: list and run pipeline."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session, get_session_optional
from services.intel_service import (
    get_intel_by_id,
    get_intel_items,
    get_intel_semantic_search,
    get_tracked_competitors,
    run_pipeline,
)

router = APIRouter(prefix="/intel", tags=["intel"])


def _intel_to_dict(item) -> dict:
    """Convert IntelItem to JSON-serializable dict."""
    return {
        "id": str(item.id),
        "competitor": item.competitor,
        "signal_type": item.signal_type,
        "threat_level": item.threat_level,
        "threat_reason": item.threat_reason,
        "summary": item.summary,
        "happyco_response": item.happyco_response,
        "confidence": item.confidence,
        "source_url": item.source_url,
        "detected_at": item.detected_at.isoformat() if item.detected_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.get("")
async def list_intel(
    session: AsyncSession | None = Depends(get_session_optional),
    competitor: str | None = Query(None, description="Filter by competitor"),
    signal_type: str | None = Query(None, description="Filter by signal type"),
    limit: int = Query(100, ge=1, le=500),
) -> dict:
    """List intel items with optional filters. Returns empty when DB is not configured or unreachable."""
    if session is None:
        return {"items": [], "count": 0}
    try:
        items = await get_intel_items(
            session, competitor=competitor, signal_type=signal_type, limit=limit
        )
        return {"items": [_intel_to_dict(i) for i in items], "count": len(items)}
    except (OSError, OperationalError):
        # DB unreachable (e.g. bad host, offline, getaddrinfo failed)
        return {"items": [], "count": 0}


@router.get("/search")
async def search_intel(
    q: str = Query(..., min_length=1, description="Search query for semantic similarity"),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """Semantic search: find intel items similar to the query (requires OpenAI embeddings)."""
    items = await get_intel_semantic_search(session, q, limit=limit)
    return {"items": [_intel_to_dict(i) for i in items], "count": len(items)}


@router.get("/signals/{signal_type}")
async def list_intel_by_signal(
    signal_type: str,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1, le=500),
) -> dict:
    """List intel items by signal type (e.g. PRODUCT_LAUNCH, PRICING_CHANGE)."""
    items = await get_intel_items(
        session, signal_type=signal_type, limit=limit
    )
    return {"items": [_intel_to_dict(i) for i in items], "count": len(items)}


@router.get("/{competitor}")
async def list_intel_by_competitor(
    competitor: str,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1, le=500),
) -> dict:
    """List intel items for a specific competitor."""
    items = await get_intel_items(
        session, competitor=competitor, limit=limit
    )
    return {"items": [_intel_to_dict(i) for i in items], "count": len(items)}


@router.get("/item/{item_id}")
async def get_intel_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Fetch a single intel item by ID."""
    item = await get_intel_by_id(session, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Intel item not found")
    return _intel_to_dict(item)


@router.post("/run")
async def run_intel_pipeline(
    competitor: str | None = Query(None, description="Run for one competitor; omit for all"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Run scrape -> analyze -> store pipeline.

    Specify ?competitor=AppFolio for one, or omit to run for all tracked competitors.
    """
    competitors = [competitor] if competitor else get_tracked_competitors()
    if not competitors:
        return {"created": 0, "message": "No competitors configured"}

    if competitor and competitor not in get_tracked_competitors():
        raise HTTPException(
            status_code=400,
            detail=f"Unknown competitor: {competitor}. Tracked: {get_tracked_competitors()}",
        )

    total_created = 0
    for comp in competitors:
        created = await run_pipeline(comp, session)
        total_created += len(created)

    return {
        "created": total_created,
        "competitors_run": competitors,
    }
