"""Pure calculation logic: name rules, timestamp parsing, slot expansion, horizon checks.

Nothing in this module touches storage, Flask, or the wall clock beyond the
`now` value callers pass in. This is what keeps it unit-testable in isolation.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

SLOT_DURATION = timedelta(minutes=30)
HORIZON = timedelta(days=28)

NAME_PATTERN = re.compile(r"^[a-z0-9-]{3,64}$")

_ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@dataclass(frozen=True)
class Slot:
    """A fixed 30-minute time slot, free until a booking claims it."""

    start: datetime
    end: datetime


@dataclass(frozen=True)
class Booking:
    """A confirmed reservation of one slot by a visitor."""

    id: str
    start: datetime
    end: datetime
    visitor_name: str


def normalize_name(raw_name: str) -> str:
    """Trim and lowercase a user-entered name. Never rewrites other characters."""
    return raw_name.strip().lower()


def is_valid_name(name: str) -> bool:
    """Return whether a normalized name satisfies the 3-64 char `[a-z0-9-]+` rule."""
    return bool(NAME_PATTERN.match(name))


def parse_utc_timestamp(value: object) -> datetime | None:
    """Parse a UTC ISO 8601 timestamp with seconds, e.g. `2026-08-01T10:00:00Z`.

    Returns None instead of raising, so callers can decide whether an
    unparseable value means `400 validation_error` or `404 not_found`.
    """
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.strptime(value, _ISO_FORMAT)
    except ValueError:
        return None
    return parsed.replace(tzinfo=UTC)


def format_utc_timestamp(instant: datetime) -> str:
    """Format a UTC datetime as ISO 8601 with seconds, e.g. `2026-08-01T10:00:00Z`."""
    return instant.astimezone(UTC).strftime(_ISO_FORMAT)


def is_on_slot_boundary(instant: datetime) -> bool:
    """Return whether a datetime falls on a 30-minute boundary with no sub-minute part."""
    return instant.minute % 30 == 0 and instant.second == 0 and instant.microsecond == 0


def horizon_end(now: datetime) -> datetime:
    """The rolling four-week horizon end, exactly 28 days after `now`."""
    return now + HORIZON


def is_within_horizon(start: datetime, end: datetime, now: datetime) -> bool:
    """Return whether [start, end] lies within [now, now + 28 days]."""
    return start >= now and end <= horizon_end(now)


def is_visible(start: datetime, now: datetime) -> bool:
    """Return whether a slot/booking starting at `start` has not yet passed.

    Time moves, so this is re-evaluated on every request rather than stored.
    """
    return start >= now


def validate_availability_range(
    start: datetime, end: datetime, now: datetime, *, allow_past: bool = False
) -> str | None:
    """Validate an availability range's bounds. Returns an error message, or None if valid.

    `allow_past` skips the "starts no earlier than now" check. It exists only
    for seed loading, which intentionally declares past entries to fixture
    "expired data is invisible" tests; the API itself never sets it.
    """
    if not is_on_slot_boundary(start) or not is_on_slot_boundary(end):
        return "Availability start and end must fall on 30-minute boundaries."
    if end <= start:
        return "The availability end must be after its start."
    if end > horizon_end(now):
        return "Availability must be within the four-week booking horizon."
    if not allow_past and start < now:
        return "Availability must be within the four-week booking horizon."
    return None


def expand_range_to_slots(start: datetime, end: datetime) -> list[Slot]:
    """Expand an availability range into consecutive fixed 30-minute slots."""
    slots: list[Slot] = []
    cursor = start
    while cursor < end:
        slot_end = cursor + SLOT_DURATION
        slots.append(Slot(start=cursor, end=slot_end))
        cursor = slot_end
    return slots


def generate_booking_id() -> str:
    """Generate an opaque, globally unique booking ID."""
    return uuid.uuid4().hex
