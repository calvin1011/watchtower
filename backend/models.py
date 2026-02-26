from datetime import date, datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IntelItem(Base):
    __tablename__ = "intel_items"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    competitor: Mapped[str] = mapped_column(String(100), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    threat_level: Mapped[str] = mapped_column(String(20), nullable=False)
    threat_reason: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    happyco_response: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Digest(Base):
    __tablename__ = "digests"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    week_of: Mapped[date] = mapped_column(Date, nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
