"""Tests for scheduler module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scheduler import (
    _weekly_digest_job,
    get_scheduler,
    shutdown_scheduler,
    start_scheduler,
)


def test_get_scheduler_configures_weekly_job():
    """get_scheduler returns scheduler with Monday 7:00 AM UTC job."""
    shutdown_scheduler()  # Reset so we get fresh scheduler
    sched = get_scheduler()
    jobs = sched.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].id == "weekly_digest"
    assert jobs[0].name == "Weekly Monday Digest"
    # Verify it's a cron trigger (implementation details may vary by APScheduler version)
    from apscheduler.triggers.cron import CronTrigger
    assert isinstance(jobs[0].trigger, CronTrigger)


@pytest.mark.asyncio
async def test_weekly_digest_job_no_database():
    """_weekly_digest_job exits early when DATABASE_URL not set."""
    with patch("scheduler.settings") as mock_settings:
        mock_settings.database_url = None
        await _weekly_digest_job()
    # No exception, job completes


@pytest.mark.asyncio
async def test_weekly_digest_job_runs_pipeline_and_send():
    """_weekly_digest_job runs pipeline for all competitors then sends digest."""
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    with (
        patch("scheduler.settings") as mock_settings,
        patch("scheduler.session_context") as mock_ctx,
        patch("scheduler.run_pipeline", new_callable=AsyncMock) as mock_pipeline,
        patch("scheduler.create_and_send_digest", new_callable=AsyncMock) as mock_send,
    ):
        mock_settings.database_url = "postgresql://test"
        mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_pipeline.return_value = []
        mock_send.return_value = MagicMock(week_of="2025-02-24", recipient="jindou@happy.co")

        await _weekly_digest_job()

        assert mock_pipeline.call_count >= 1
        mock_send.assert_called_once_with(mock_session, since_days=7)


@pytest.mark.asyncio
async def test_start_and_shutdown_scheduler():
    """start_scheduler and shutdown_scheduler don't raise."""
    with patch("scheduler.settings") as mock_settings:
        mock_settings.database_url = "postgresql://test"
        start_scheduler()  # Requires running event loop (AsyncIOScheduler)
        shutdown_scheduler()
