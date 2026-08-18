"""Pure UTC slot calculation and validation."""

from datetime import UTC, datetime, timedelta

SLOT_DURATION = timedelta(minutes=30)
HORIZON_DURATION = timedelta(days=28)


def parse_timestamp(value: object) -> datetime:
    """Parse a UTC ISO-8601 timestamp with a Z suffix."""
    if not isinstance(value, str):
        raise ValueError("Timestamp must be a string.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Timestamp must be a valid UTC ISO 8601 value.") from error
    if parsed.tzinfo != UTC:
        raise ValueError("Timestamp must be expressed in UTC.")
    return parsed


def format_timestamp(value: datetime) -> str:
    """Format a UTC timestamp using the API representation."""
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def expand_range(start: datetime, end: datetime) -> list[datetime]:
    """Expand a bounded range into 30-minute slot start times."""
    if not is_slot_boundary(start) or not is_slot_boundary(end):
        raise ValueError("Availability bounds must fall on 30-minute boundaries.")
    if end <= start:
        raise ValueError("The availability end must be after its start.")
    result: list[datetime] = []
    current = start
    while current < end:
        result.append(current)
        current += SLOT_DURATION
    return result


def validate_horizon(start: datetime, end: datetime, now: datetime) -> None:
    """Ensure an availability range is inside the rolling four-week horizon."""
    limit = now + HORIZON_DURATION
    if start < now or end > limit:
        raise ValueError("Availability must be within the next four weeks.")


def is_slot_boundary(value: datetime) -> bool:
    """Return whether the timestamp is on a 30-minute UTC boundary."""
    return value.second == 0 and value.microsecond == 0 and value.minute in (0, 30)


def is_past(start: datetime, now: datetime) -> bool:
    """Return whether a slot has already started."""
    return start <= now
