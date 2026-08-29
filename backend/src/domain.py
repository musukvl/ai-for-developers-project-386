"""Booking window, slot grid, and occupancy rules for Calls Calendar.

Slots are never stored. Each request generates the 14-day UTC grid for an
event type's duration and subtracts intervals occupied by any booking.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

WINDOW_DAYS = 14

_ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@dataclass(frozen=True)
class EventType:
    """Catalog entry a guest picks before booking."""

    id: str
    title: str
    description: str
    duration_minutes: int


@dataclass(frozen=True)
class Slot:
    """A generated free interval for one event type."""

    start: datetime
    end: datetime


@dataclass(frozen=True)
class Booking:
    """A reserved clock interval, tagged with the event type and guest name."""

    id: str
    event_type_id: str
    event_type_title: str
    start: datetime
    end: datetime
    guest_name: str


def utc_now() -> datetime:
    """Return the current instant in UTC."""
    return datetime.now(UTC)


def window_last_date(now: datetime) -> date:
    """Return the last UTC calendar date included in the 14-day window."""
    return now.date() + timedelta(days=WINDOW_DAYS - 1)


def is_visible(start: datetime, now: datetime) -> bool:
    """Return True when `start` has not already passed."""
    return start >= now


def is_within_window(start: datetime, now: datetime) -> bool:
    """Return True when `start` is visible and falls on today through today+13 UTC."""
    if not is_visible(start, now):
        return False
    return now.date() <= start.date() <= window_last_date(now)


def format_utc_timestamp(value: datetime) -> str:
    """Format a UTC instant as `YYYY-MM-DDTHH:MM:SSZ`."""
    return value.astimezone(UTC).strftime(_ISO_FORMAT)


def parse_utc_timestamp(value: object) -> datetime | None:
    """Parse an ISO-8601 UTC timestamp. Returns None when the value is unusable."""
    if not isinstance(value, str) or not value:
        return None

    try:
        if value.endswith("Z"):
            parsed = datetime.fromisoformat(value[:-1] + "+00:00")
        else:
            parsed = datetime.fromisoformat(value)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC)


def generate_booking_id() -> str:
    """Return an opaque UUID4 hex string."""
    return uuid.uuid4().hex


def slot_end(start: datetime, duration_minutes: int) -> datetime:
    """Return the exclusive end of a slot starting at `start`."""
    return start + timedelta(minutes=duration_minutes)


def is_on_duration_grid(start: datetime, duration_minutes: int) -> bool:
    """Return True when `start` is a same-day grid point for `duration_minutes`.

    Grid points are consecutive multiples of the duration from 00:00 UTC.
    A candidate that would end on the next UTC date is not on the grid.
    """
    if duration_minutes < 1:
        return False
    if start.second != 0 or start.microsecond != 0:
        return False

    minutes_from_midnight = start.hour * 60 + start.minute
    if minutes_from_midnight % duration_minutes != 0:
        return False

    end = slot_end(start, duration_minutes)
    return end.date() == start.date()


def intervals_overlap(
    left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime
) -> bool:
    """Return True when two half-open intervals `[start, end)` overlap."""
    return left_start < right_end and right_start < left_end


def generate_slots(
    duration_minutes: int,
    now: datetime,
    occupied: list[tuple[datetime, datetime]],
) -> list[Slot]:
    """Generate free slots for `duration_minutes` across the 14-day window.

    Occupied intervals of any event type are subtracted. Results are sorted
    ascending by start.
    """
    slots: list[Slot] = []
    today = now.date()

    for day_offset in range(WINDOW_DAYS):
        day = today + timedelta(days=day_offset)
        slots.extend(_slots_for_day(day, duration_minutes, now, occupied))

    return slots


def _slots_for_day(
    day: date,
    duration_minutes: int,
    now: datetime,
    occupied: list[tuple[datetime, datetime]],
) -> list[Slot]:
    """Fill one UTC calendar day with consecutive same-day slots of `duration_minutes`."""
    slots: list[Slot] = []
    cursor = datetime(day.year, day.month, day.day, tzinfo=UTC)
    delta = timedelta(minutes=duration_minutes)

    while True:
        end = cursor + delta
        if end.date() != cursor.date():
            break
        if cursor >= now and not _is_occupied(cursor, end, occupied):
            slots.append(Slot(start=cursor, end=end))
        cursor = end

    return slots


def _is_occupied(
    start: datetime, end: datetime, occupied: list[tuple[datetime, datetime]]
) -> bool:
    return any(
        intervals_overlap(start, end, booked_start, booked_end)
        for booked_start, booked_end in occupied
    )


def classify_booking_slot(
    event_type: EventType,
    slot_start: datetime,
    existing_bookings: list[Booking],
    now: datetime,
) -> str | Slot:
    """Return a free `Slot` or a 409 error code, using the contract's check order.

    Order after the event type is known: occupied, outside window, mismatch.
    """
    end = slot_end(slot_start, event_type.duration_minutes)

    if any(
        intervals_overlap(slot_start, end, booking.start, booking.end)
        for booking in existing_bookings
    ):
        return "slot_occupied"

    if not is_within_window(slot_start, now):
        return "slot_outside_window"

    if not is_on_duration_grid(slot_start, event_type.duration_minutes):
        return "slot_mismatch"

    return Slot(start=slot_start, end=end)
