"""Helpers for building UTC timestamps relative to 'now' in integration tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.domain import format_utc_timestamp


def utc_today_at(hour: int, minute: int, day_offset: int = 0) -> datetime:
    """Return a UTC datetime on today+offset at HH:MM."""
    now = datetime.now(UTC)
    day = now.date() + timedelta(days=day_offset)
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=UTC)


def iso(value: datetime) -> str:
    """Format a datetime as the API's UTC ISO-8601 string."""
    return format_utc_timestamp(value)
