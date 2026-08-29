"""Load and validate YAML seed data into in-memory storage."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from src.domain import (
    Booking,
    EventType,
    generate_booking_id,
    intervals_overlap,
    is_on_duration_grid,
    slot_end,
    utc_now,
)
from src.logging_setup import logger
from src.storage import EventTypeExistsError, Storage

_TIME_FORMAT = "%H:%M"


class SeedError(Exception):
    """Raised when the seed file is missing, malformed, or violates booking rules."""


def load_seed(storage: Storage, seed_file: str, now: datetime | None = None) -> None:
    """Populate `storage` from `seed_file`. Invalid data aborts startup."""
    instant = now or utc_now()
    payload = _read_yaml(seed_file)

    owner = payload.get("owner")
    if not isinstance(owner, str) or not owner.strip():
        raise SeedError("Seed field 'owner' must be a non-empty string.")
    storage.owner = owner.strip()

    event_types = payload.get("eventTypes")
    if not isinstance(event_types, list):
        raise SeedError("Seed field 'eventTypes' must be a list.")
    for entry in event_types:
        _load_event_type(storage, entry)

    bookings = payload.get("bookings", [])
    if bookings is None:
        bookings = []
    if not isinstance(bookings, list):
        raise SeedError("Seed field 'bookings' must be a list.")

    loaded_bookings: list[Booking] = []
    for entry in bookings:
        booking = _build_booking(storage, entry, instant)
        for existing in loaded_bookings:
            if intervals_overlap(booking.start, booking.end, existing.start, existing.end):
                raise SeedError(
                    f"Seed booking {booking.id!r} overlaps booking {existing.id!r}."
                )
        loaded_bookings.append(booking)
        storage.seed_booking(booking)

    logger.bind(
        event="seed.loaded",
        seed_file=seed_file,
        event_type_count=len(storage.list_event_types()),
        booking_count=len(loaded_bookings),
    ).info("seed.loaded")


def _read_yaml(seed_file: str) -> dict:
    path = Path(seed_file)
    if not path.is_file():
        raise SeedError(f"Seed file {seed_file!r} does not exist.")

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SeedError(f"Seed file {seed_file!r} is not valid YAML: {exc}") from exc

    if not isinstance(loaded, dict):
        raise SeedError("Seed file must contain a mapping at the top level.")
    return loaded


def _load_event_type(storage: Storage, entry: object) -> None:
    if not isinstance(entry, dict):
        raise SeedError("Each event type must be a mapping.")

    event_type_id = _required_string(entry, "id")
    title = _required_string(entry, "title")
    description = entry.get("description")
    if not isinstance(description, str):
        raise SeedError(f"Event type {event_type_id!r} is missing a string 'description'.")
    duration = entry.get("durationMinutes")
    if not isinstance(duration, int) or isinstance(duration, bool) or duration < 1:
        raise SeedError(f"Event type {event_type_id!r} has an invalid durationMinutes.")

    try:
        storage.create_event_type(
            EventType(
                id=event_type_id,
                title=title,
                description=description,
                duration_minutes=duration,
            )
        )
    except EventTypeExistsError as exc:
        raise SeedError(f"Duplicate event type id {event_type_id!r}.") from exc


def _build_booking(storage: Storage, entry: object, now: datetime) -> Booking:
    if not isinstance(entry, dict):
        raise SeedError("Each booking must be a mapping.")

    event_type_id = _required_string(entry, "eventTypeId")
    event_type = storage.get_event_type(event_type_id)
    if event_type is None:
        raise SeedError(f"Seed booking references unknown event type {event_type_id!r}.")

    guest_name = _required_string(entry, "guestName")
    day_offset = entry.get("day")
    if not isinstance(day_offset, int) or isinstance(day_offset, bool):
        raise SeedError("Seed booking 'day' must be an integer offset from today.")

    start = _resolve_instant(now, day_offset, entry.get("start"))
    if not is_on_duration_grid(start, event_type.duration_minutes):
        raise SeedError(
            f"Seed booking start {start.isoformat()} is not on the "
            f"{event_type.duration_minutes}-minute grid."
        )

    booking_id = entry.get("id")
    if booking_id is None:
        booking_id = generate_booking_id()
    elif not isinstance(booking_id, str) or not booking_id:
        raise SeedError("Seed booking 'id' must be a non-empty string when provided.")

    return Booking(
        id=booking_id,
        event_type_id=event_type.id,
        event_type_title=event_type.title,
        start=start,
        end=slot_end(start, event_type.duration_minutes),
        guest_name=guest_name,
    )


def _required_string(entry: dict, key: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SeedError(f"Seed field {key!r} must be a non-empty string.")
    return value.strip()


def _resolve_instant(now: datetime, day_offset: int, time_str: object) -> datetime:
    if not isinstance(time_str, str):
        raise SeedError("Seed booking 'start' must be an HH:MM string.")
    try:
        parsed_time = datetime.strptime(time_str, _TIME_FORMAT).time()
    except ValueError as exc:
        raise SeedError(f"Seed booking start {time_str!r} is not HH:MM.") from exc

    day = now.date() + timedelta(days=day_offset)
    return datetime(
        day.year,
        day.month,
        day.day,
        parsed_time.hour,
        parsed_time.minute,
        tzinfo=UTC,
    )
