"""Competitors API: CRUD for tracked competitors."""

import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Competitor

router = APIRouter(prefix="/competitors", tags=["competitors"])


def _slug_from_name(name: str) -> str:
    """Derive URL-safe slug: lowercase, non-alphanumeric -> hyphens, strip."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "competitor"


def _competitor_to_dict(c: Competitor) -> dict:
    """Convert Competitor to JSON-serializable dict."""
    return {
        "id": str(c.id),
        "name": c.name,
        "slug": c.slug,
        "website_url": c.website_url,
        "blog_url": c.blog_url,
        "g2_slug": c.g2_slug,
        "capterra_slug": c.capterra_slug,
        "is_active": c.is_active,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


class CompetitorCreate(BaseModel):
    name: str = Field(..., min_length=1)
    slug: str | None = Field(None, description="URL-safe slug; derived from name if omitted")
    website_url: str | None = None
    blog_url: str | None = None
    g2_slug: str | None = None
    capterra_slug: str | None = None


class CompetitorUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    website_url: str | None = None
    blog_url: str | None = None
    g2_slug: str | None = None
    capterra_slug: str | None = None
    is_active: bool | None = None


async def _get_competitor_by_id(session: AsyncSession, id: UUID) -> Competitor | None:
    result = await session.execute(select(Competitor).where(Competitor.id == id))
    return result.scalar_one_or_none()


@router.get("")
async def list_competitors(
    session: AsyncSession = Depends(get_session),
    include_inactive: bool = Query(False, description="Include inactive (soft-deleted) competitors"),
) -> dict:
    """List competitors. By default only active; set include_inactive=true for all."""
    stmt = select(Competitor).order_by(Competitor.name)
    if not include_inactive:
        stmt = stmt.where(Competitor.is_active == True)
    result = await session.execute(stmt)
    competitors = list(result.scalars().all())
    return {"competitors": [_competitor_to_dict(c) for c in competitors], "count": len(competitors)}


@router.post("", status_code=201)
async def create_competitor(
    body: CompetitorCreate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Create a competitor. Slug is derived from name if not provided."""
    slug = (body.slug or _slug_from_name(body.name)).strip() or _slug_from_name(body.name)
    existing = await session.execute(select(Competitor).where(Competitor.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Competitor with slug '{slug}' already exists")
    competitor = Competitor(
        name=body.name.strip(),
        slug=slug,
        website_url=body.website_url.strip() if body.website_url else None,
        blog_url=body.blog_url.strip() if body.blog_url else None,
        g2_slug=body.g2_slug.strip() if body.g2_slug else None,
        capterra_slug=body.capterra_slug.strip() if body.capterra_slug else None,
    )
    session.add(competitor)
    await session.commit()
    await session.refresh(competitor)
    return _competitor_to_dict(competitor)


@router.patch("/{id}")
async def update_competitor(
    id: UUID,
    body: CompetitorUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Update a competitor. Soft delete is done via DELETE endpoint."""
    competitor = await _get_competitor_by_id(session, id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    if body.name is not None:
        competitor.name = body.name.strip()
    if body.website_url is not None:
        competitor.website_url = body.website_url.strip() or None
    if body.blog_url is not None:
        competitor.blog_url = body.blog_url.strip() or None
    if body.g2_slug is not None:
        competitor.g2_slug = body.g2_slug.strip() or None
    if body.capterra_slug is not None:
        competitor.capterra_slug = body.capterra_slug.strip() or None
    if body.is_active is not None:
        competitor.is_active = body.is_active
    await session.commit()
    await session.refresh(competitor)
    return _competitor_to_dict(competitor)


@router.delete("/{id}", status_code=204)
async def delete_competitor(
    id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Soft delete: set is_active = False."""
    competitor = await _get_competitor_by_id(session, id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    competitor.is_active = False
    await session.commit()
