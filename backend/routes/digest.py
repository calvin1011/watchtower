"""Digest API: send and list digests."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_session
from digest import create_and_send_digest
from models import Digest

router = APIRouter(prefix="/digest", tags=["digest"])


def _digest_to_dict(d: Digest) -> dict:
    """Convert Digest to JSON-serializable dict."""
    return {
        "id": str(d.id),
        "week_of": d.week_of.isoformat() if d.week_of else None,
        "content": d.content,
        "sent_at": d.sent_at.isoformat() if d.sent_at else None,
        "recipient": d.recipient,
    }


@router.post("/send")
async def send_digest(
    session: AsyncSession = Depends(get_session),
    recipient: str | None = Query(None, description="Override recipient (default: DIGEST_RECIPIENT)"),
    since_days: int = Query(7, ge=1, le=90, description="Include intel from last N days"),
) -> dict:
    """
    Build and send Monday digest via Resend.

    Requires RESEND_API_KEY in env. Uses DIGEST_RECIPIENT if recipient not provided.
    """
    if not settings.resend_api_key:
        raise HTTPException(
            status_code=503,
            detail="RESEND_API_KEY not configured. Cannot send digest.",
        )
    digest = await create_and_send_digest(
        session,
        recipient=recipient,
        since_days=since_days,
    )
    if not digest:
        raise HTTPException(
            status_code=502,
            detail="Failed to send email via Resend.",
        )
    return {"message": "Digest sent", "digest": _digest_to_dict(digest)}


@router.get("/history")
async def get_digest_history(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """List past digests, most recent first."""
    stmt = (
        select(Digest)
        .order_by(Digest.sent_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    digests = list(result.scalars().all())
    return {
        "digests": [_digest_to_dict(d) for d in digests],
        "count": len(digests),
    }
