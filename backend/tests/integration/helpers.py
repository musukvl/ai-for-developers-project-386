"""Small helpers for building horizon-safe availability ranges in integration tests.

Tests cannot hardcode absolute dates, because the API validates every range
against the rolling horizon measured from the real wall clock at request
time. These helpers compute slot-boundary timestamps relative to "now".
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.domain import format_utc_timestamp


def next_slot_boundary(offset: timedelta) -> datetime:
    """Round `now + offset` up to the next 30-minute boundary."""
    target = datetime.now(UTC) + offset
    minute = 0 if target.minute < 30 else 30
    rounded = target.replace(minute=minute, second=0, microsecond=0)
    if rounded <= datetime.now(UTC):
        rounded += timedelta(minutes=30)
    return rounded


def future_range(
    start_offset: timedelta = timedelta(days=1), duration: timedelta = timedelta(hours=1)
) -> tuple[datetime, datetime]:
    """A valid, within-horizon (start, end) pair suitable for the availability API."""
    start = next_slot_boundary(start_offset)
    return start, start + duration


def iso(instant: datetime) -> str:
    return format_utc_timestamp(instant)


def day_offset_instant(day_offset: int, hour: int, minute: int) -> datetime:
    """Resolve a `day`/`HH:MM` pair the same way the seed loader does, for test fixtures."""
    target_date = datetime.now(UTC).date() + timedelta(days=day_offset)
    return datetime(
        target_date.year, target_date.month, target_date.day, hour, minute, tzinfo=UTC
    )
