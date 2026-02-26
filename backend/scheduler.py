"""Weekly scheduler for Monday morning digest: scrape -> analyze -> store -> send_digest."""

import logging
from datetime import UTC

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings
from database import session_context
from digest import create_and_send_digest
from services.intel_service import get_tracked_competitors, run_pipeline

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _weekly_digest_job() -> None:
    """
    Run the full pipeline: scrape all competitors -> analyze -> store -> send digest.

    Runs every Monday at 7:00 AM (UTC by default; configure timezone in trigger if needed).
    """
    if not settings.database_url:
        logger.warning("Skipping weekly digest: DATABASE_URL not configured")
        return

    async with session_context() as session:
        # 1. Scrape -> Analyze -> Store for each competitor
        competitors = get_tracked_competitors()
        total_created = 0
        for competitor in competitors:
            try:
                created = await run_pipeline(competitor, session)
                total_created += len(created)
                if created:
                    logger.info("Pipeline created %d intel items for %s", len(created), competitor)
            except Exception as e:
                logger.exception("Pipeline failed for %s: %s", competitor, e)

        logger.info("Pipeline complete: %d total intel items from %d competitors", total_created, len(competitors))

        # 2. Build and send digest email
        digest = await create_and_send_digest(session, since_days=7)
        if digest:
            logger.info("Digest sent for week of %s to %s", digest.week_of, digest.recipient)
        else:
            logger.warning("Digest send failed or Resend not configured")


def get_scheduler() -> AsyncIOScheduler:
    """Create and configure the scheduler (call once at startup)."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = AsyncIOScheduler(timezone=UTC)
    # Every Monday at 7:00 AM UTC
    _scheduler.add_job(
        _weekly_digest_job,
        CronTrigger(day_of_week="mon", hour=7, minute=0, timezone=UTC),
        id="weekly_digest",
        name="Weekly Monday Digest",
    )
    return _scheduler


def start_scheduler() -> None:
    """Start the scheduler (call from app lifespan)."""
    if not settings.database_url:
        logger.info("Scheduler not started: DATABASE_URL not configured")
        return
    sched = get_scheduler()
    sched.start()
    logger.info("Scheduler started: weekly digest Mondays 7:00 AM UTC")


def shutdown_scheduler() -> None:
    """Shutdown the scheduler (call from app lifespan)."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=True)
        _scheduler = None
        logger.info("Scheduler stopped")
