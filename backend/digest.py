"""Build and send Monday morning competitive intel digest via Resend."""

from collections import defaultdict
from datetime import date, datetime, timedelta, UTC
from typing import Any

import resend
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models import Digest, IntelItem
from services.intel_service import get_intel_items


def _item_to_dict(item: IntelItem) -> dict[str, Any]:
    """Convert IntelItem to serializable dict for digest content."""
    return {
        "id": str(item.id),
        "competitor": item.competitor,
        "signal_type": item.signal_type,
        "threat_level": item.threat_level,
        "threat_reason": item.threat_reason,
        "summary": item.summary,
        "happyco_response": item.happyco_response,
        "source_url": item.source_url,
        "detected_at": item.detected_at.isoformat() if item.detected_at else None,
    }


def _group_by_threat(items: list[IntelItem]) -> dict[str, list[IntelItem]]:
    """Group intel items by threat level (HIGH, MEDIUM, LOW)."""
    grouped: dict[str, list[IntelItem]] = defaultdict(list)
    order = ("HIGH", "MEDIUM", "LOW")
    for level in order:
        grouped[level] = []
    for item in items:
        level = (item.threat_level or "LOW").upper()
        if level not in grouped:
            grouped[level] = []
        grouped[level].append(item)
    # Return in canonical order, only non-empty
    return {k: grouped[k] for k in order if grouped.get(k)}


def _build_html_email(content: dict[str, Any], week_of: date) -> str:
    """Build HTML body for digest email."""
    grouped = content.get("grouped", {})
    subject_date = week_of.strftime("%B %d, %Y")

    sections = []
    for level in ("HIGH", "MEDIUM", "LOW"):
        items = grouped.get(level, [])
        if not items:
            continue
        color = {"HIGH": "#dc2626", "MEDIUM": "#ea580c", "LOW": "#ca8a04"}.get(
            level, "#6b7280"
        )
        sections.append(
            f'<h2 style="color:{color}; margin-top:24px; margin-bottom:12px;">{level}</h2>'
        )
        for it in items:
            link = f'<a href="{it.get("source_url") or "#"}">Source</a>' if it.get("source_url") else ""
            sections.append(
                f"""
                <div style="margin-bottom:16px; padding:12px; background:#f9fafb; border-radius:8px;">
                    <p style="margin:0 0 4px;"><strong>{it.get("competitor", "")}</strong> · {it.get("signal_type", "")}</p>
                    <p style="margin:0 0 8px;">{it.get("summary", "")}</p>
                    <p style="margin:0 0 4px; color:#374151;"><em>Threat:</em> {it.get("threat_reason", "")}</p>
                    <p style="margin:0; color:#059669;"><strong>HappyCo response:</strong> {it.get("happyco_response", "")}</p>
                    {f'<p style="margin:8px 0 0; font-size:12px;">{link}</p>' if link else ""}
                </div>
                """
            )

    body = "\n".join(sections) if sections else "<p>No new intel this week.</p>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:sans-serif; max-width:640px; margin:0 auto; padding:24px;">
        <h1 style="color:#111;">Watchtower Competitive Intel — Week of {subject_date}</h1>
        <p style="color:#6b7280;">Monday morning briefing from the HappyCo Competitive Intelligence Agent.</p>
        {body}
        <hr style="margin-top:32px; border:none; border-top:1px solid #e5e7eb;">
        <p style="font-size:12px; color:#9ca3af;">Sent by Watchtower. Not for external distribution.</p>
    </body>
    </html>
    """


async def build_digest(
    session: AsyncSession,
    *,
    since_days: int = 7,
    limit: int = 100,
) -> tuple[dict[str, Any], date]:
    """
    Build digest content from recent intel items, grouped by threat level.

    Returns (content_dict for JSONB, week_of date).
    """
    items = await get_intel_items(session, limit=limit)
    # Filter to items from the last N days
    cutoff = datetime.now(UTC) - timedelta(days=since_days)
    recent = [i for i in items if i.detected_at and i.detected_at >= cutoff]

    items_to_include = recent if recent else items  # Use recent, or all if none in window
    grouped = _group_by_threat(items_to_include)
    week_of = date.today() - timedelta(days=date.today().weekday())  # Monday

    content: dict[str, Any] = {
        "week_of": week_of.isoformat(),
        "grouped": {
            level: [_item_to_dict(it) for it in items]
            for level, items in grouped.items()
        },
        "total_items": sum(len(v) for v in grouped.values()),
    }
    return content, week_of


def send_digest_email(
    recipient: str,
    subject: str,
    html: str,
) -> dict[str, Any] | None:
    """
    Send digest email via Resend.

    Returns Resend response dict on success, None on failure.
    """
    if not settings.resend_api_key:
        return None
    resend.api_key = settings.resend_api_key

    params: dict[str, Any] = {
        "from": "Watchtower <onboarding@resend.dev>",
        "to": [recipient],
        "subject": subject,
        "html": html,
    }
    try:
        result = resend.Emails.send(params)
        return result
    except Exception:
        return None


async def create_and_send_digest(
    session: AsyncSession,
    recipient: str | None = None,
    *,
    since_days: int = 7,
) -> Digest | None:
    """
    Build digest, send email via Resend, and persist Digest record.

    Returns the created Digest on success, None on failure.
    """
    to = recipient or settings.digest_recipient
    content, week_of = await build_digest(session, since_days=since_days)
    html = _build_html_email(content, week_of)
    subject = f"Watchtower Intel Digest — Week of {week_of.strftime('%B %d, %Y')}"

    result = send_digest_email(to, subject, html)
    if not result:
        return None

    digest = Digest(
        week_of=week_of,
        content=content,
        recipient=to,
    )
    session.add(digest)
    await session.commit()
    await session.refresh(digest)
    return digest
