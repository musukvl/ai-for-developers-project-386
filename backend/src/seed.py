"""YAML seed-file loading with relative UTC day expansion."""

from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from uuid import uuid4

import yaml

from .logging_setup import log_event
from .models import Booking
from .names import validate_name
from .slots import expand_range, is_slot_boundary
from .storage import CalendarStore


def load_seed(store: CalendarStore, seed_file: Path, now: datetime | None = None) -> None:
    """Load a complete seed fixture into an empty application store."""
    load_time = now or datetime.now(UTC)
    try:
        contents = yaml.safe_load(seed_file.read_text())
    except (OSError, yaml.YAMLError) as error:
        raise RuntimeError(f"Unable to read seed file {seed_file}: {error}") from error
    if not isinstance(contents, dict):
        raise RuntimeError("Seed root must be a mapping.")

    users = contents.get("users", [])
    calendars = contents.get("calendars", [])
    if not isinstance(users, list) or not isinstance(calendars, list):
        raise RuntimeError("Seed users and calendars must be lists.")
    known_users: set[str] = set()
    for position, name in enumerate(users):
        normalized = _validate_seed_name(name, f"users[{position}]")
        if normalized in known_users:
            raise RuntimeError(f"Duplicate seed user at users[{position}].")
        known_users.add(normalized)
        store.register_user(normalized)

    for position, definition in enumerate(calendars):
        _load_calendar(store, definition, known_users, load_time, position)
    log_event("seed.loaded", seed_file=str(seed_file), users=len(users), calendars=len(calendars))


def expand_seed_range(definition: dict[object, object], load_time: datetime) -> list[datetime]:
    """Expand one relative-day availability item into UTC slot starts."""
    day = definition.get("day")
    start_text = definition.get("start")
    end_text = definition.get("end")
    if not isinstance(day, int) or isinstance(day, bool):
        raise ValueError("Seed day must be an integer.")
    start = _relative_timestamp(day, start_text, load_time)
    end = _relative_timestamp(day, end_text, load_time)
    return expand_range(start, end)


def _load_calendar(
    store: CalendarStore,
    definition: object,
    known_users: set[str],
    load_time: datetime,
    position: int,
) -> None:
    if not isinstance(definition, dict):
        raise RuntimeError(f"calendars[{position}] must be a mapping.")
    owner_id = _validate_seed_name(definition.get("ownerId"), f"calendars[{position}].ownerId")
    if owner_id not in known_users:
        raise RuntimeError(f"calendars[{position}].ownerId must appear in users.")
    try:
        store.create_calendar(owner_id)
    except Exception as error:
        raise RuntimeError(f"Invalid calendar at calendars[{position}]: {error}") from error
    availability = definition.get("availability", [])
    bookings = definition.get("bookings", [])
    if not isinstance(availability, list) or not isinstance(bookings, list):
        raise RuntimeError(f"calendars[{position}] availability and bookings must be lists.")
    for range_position, period in enumerate(availability):
        if not isinstance(period, dict):
            raise RuntimeError(f"availability[{range_position}] must be a mapping.")
        try:
            starts = expand_seed_range(period, load_time)
        except ValueError as error:
            raise RuntimeError(f"Invalid availability[{range_position}]: {error}") from error
        store.add_slots(owner_id, starts)
    calendar = store.calendar_for(owner_id)
    for booking_position, entry in enumerate(bookings):
        _load_booking(
            store, calendar.slots, owner_id, entry, known_users, load_time, booking_position
        )


def _load_booking(
    store: CalendarStore,
    slots: set[datetime],
    owner_id: str,
    entry: object,
    known_users: set[str],
    load_time: datetime,
    position: int,
) -> None:
    if not isinstance(entry, dict):
        raise RuntimeError(f"bookings[{position}] must be a mapping.")
    visitor_name = _validate_seed_name(
        entry.get("visitorName"), f"bookings[{position}].visitorName"
    )
    if visitor_name not in known_users:
        raise RuntimeError(f"bookings[{position}].visitorName must appear in users.")
    try:
        start = _relative_timestamp(entry.get("day"), entry.get("start"), load_time)
    except ValueError as error:
        raise RuntimeError(f"Invalid bookings[{position}]: {error}") from error
    if not is_slot_boundary(start) or start not in slots:
        raise RuntimeError(f"bookings[{position}].start must name a published slot.")
    booking_id = entry.get("id", uuid4().hex)
    if not isinstance(booking_id, str) or not booking_id:
        raise RuntimeError(f"bookings[{position}].id must be a non-empty string.")
    store.add_seed_booking(owner_id, Booking(id=booking_id, start=start, visitor_name=visitor_name))


def _relative_timestamp(day: object, value: object, load_time: datetime) -> datetime:
    if not isinstance(day, int) or isinstance(day, bool):
        raise ValueError("Seed day must be an integer.")
    if not isinstance(value, str):
        raise ValueError("Seed time must be an HH:MM string.")
    try:
        parsed_time = time.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Seed time must be an HH:MM string.") from error
    if parsed_time.second != 0 or parsed_time.microsecond != 0:
        raise ValueError("Seed time must be on a 30-minute boundary.")
    result = datetime.combine(load_time.date() + timedelta(days=day), parsed_time, tzinfo=UTC)
    if not is_slot_boundary(result):
        raise ValueError("Seed time must be on a 30-minute boundary.")
    return result


def _validate_seed_name(value: object, location: str) -> str:
    try:
        normalized = validate_name(value)
    except ValueError as error:
        raise RuntimeError(f"Invalid name at {location}: {error}") from error
    if normalized != value:
        raise RuntimeError(f"Seed name at {location} must already be normalized.")
    return normalized
