"""Loads seed YAML into in-memory storage at startup.

Seed times are declared relative to load time (`day` offset + `HH:MM` time
of day) and expanded to absolute UTC slots here, using the same domain
functions the API uses, so a seeded image never boots with data outside the
rules the API enforces. Startup fails loudly on any violation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import yaml

from src.domain import (
    SLOT_DURATION,
    Booking,
    Slot,
    expand_range_to_slots,
    generate_booking_id,
    is_on_slot_boundary,
    is_valid_name,
    validate_availability_range,
)
from src.logging_setup import logger
from src.storage import CalendarExistsError, Storage


class SeedError(Exception):
    """Raised when the seed file is missing, malformed, or violates domain rules."""


@dataclass
class _CalendarSeed:
    owner_id: str
    slots_by_start: dict[datetime, Slot]
    bookings: list[Booking]


def load_seed(storage: Storage, seed_file: str, now: datetime | None = None) -> None:
    """Populate `storage` from a seed YAML file. Raises SeedError on any violation."""
    now = now or datetime.now(UTC)
    data = _read_yaml(seed_file)

    users = data.get("users") or []
    _load_users(storage, users)

    calendar_entries = data.get("calendars") or []
    for entry in calendar_entries:
        calendar_seed = _build_calendar_seed(entry, users, now)
        try:
            storage.create_calendar(calendar_seed.owner_id)
        except CalendarExistsError as exc:
            raise SeedError(
                f"Seed declares more than one calendar for owner {calendar_seed.owner_id!r}."
            ) from exc
        storage.seed_calendar(
            calendar_seed.owner_id,
            list(calendar_seed.slots_by_start.values()),
            calendar_seed.bookings,
        )

    logger.bind(
        event="seed.loaded",
        seed_file=seed_file,
        user_count=len(users),
        calendar_count=len(calendar_entries),
    ).info("seed.loaded")


def _read_yaml(seed_file: str) -> dict:
    try:
        with open(seed_file, encoding="utf-8") as handle:
            raw_text = handle.read()
    except OSError as exc:
        raise SeedError(f"Cannot read seed file '{seed_file}': {exc}") from exc

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise SeedError(f"Seed file '{seed_file}' is not valid YAML: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise SeedError(f"Seed file '{seed_file}' must contain a mapping at the top level.")
    return data


def _load_users(storage: Storage, users: list) -> None:
    for raw_name in users:
        if not isinstance(raw_name, str) or not is_valid_name(raw_name):
            raise SeedError(f"Seed user {raw_name!r} is not a valid normalized name.")
        storage.register_user(raw_name)


def _build_calendar_seed(entry: dict, users: list, now: datetime) -> _CalendarSeed:
    if not isinstance(entry, dict):
        raise SeedError(f"Seed calendar entry {entry!r} must be a mapping.")

    owner_id = entry.get("ownerId")
    if not isinstance(owner_id, str) or not is_valid_name(owner_id):
        raise SeedError(f"Seed calendar ownerId {owner_id!r} is not a valid normalized name.")
    if owner_id not in users:
        raise SeedError(f"Seed calendar owner {owner_id!r} must be declared in users.")

    slots_by_start: dict[datetime, Slot] = {}
    for availability_entry in entry.get("availability") or []:
        start, end = _resolve_availability_bounds(availability_entry, now, owner_id)
        error = validate_availability_range(start, end, now, allow_past=True)
        if error is not None:
            raise SeedError(f"Seed availability for {owner_id!r} is invalid: {error}")
        for slot in expand_range_to_slots(start, end):
            slots_by_start[slot.start] = slot

    bookings: list[Booking] = []
    for booking_entry in entry.get("bookings") or []:
        booking = _resolve_booking(booking_entry, slots_by_start, users, now, owner_id)
        del slots_by_start[booking.start]
        bookings.append(booking)

    return _CalendarSeed(owner_id=owner_id, slots_by_start=slots_by_start, bookings=bookings)


def _resolve_availability_bounds(
    entry: dict, now: datetime, owner_id: str
) -> tuple[datetime, datetime]:
    if not isinstance(entry, dict):
        raise SeedError(f"Seed availability entry {entry!r} for {owner_id!r} must be a mapping.")
    day = entry.get("day")
    if not isinstance(day, int) or isinstance(day, bool):
        raise SeedError(f"Seed availability 'day' {day!r} for {owner_id!r} must be an integer.")
    start = _resolve_instant(now, day, entry.get("start"), owner_id)
    end = _resolve_instant(now, day, entry.get("end"), owner_id)
    return start, end


def _resolve_booking(
    entry: dict, slots_by_start: dict[datetime, Slot], users: list, now: datetime, owner_id: str
) -> Booking:
    if not isinstance(entry, dict):
        raise SeedError(f"Seed booking entry {entry!r} for {owner_id!r} must be a mapping.")
    day = entry.get("day")
    if not isinstance(day, int) or isinstance(day, bool):
        raise SeedError(f"Seed booking 'day' {day!r} for {owner_id!r} must be an integer.")
    start = _resolve_instant(now, day, entry.get("start"), owner_id)

    visitor_name = entry.get("visitorName")
    if not isinstance(visitor_name, str) or visitor_name not in users:
        raise SeedError(
            f"Seed booking visitorName {visitor_name!r} for {owner_id!r} must be declared in users."
        )

    if start not in slots_by_start:
        raise SeedError(
            f"Seed booking for {owner_id!r} at {start.isoformat()} "
            "does not land on a published slot."
        )

    booking_id = entry.get("id") or generate_booking_id()
    if not isinstance(booking_id, str):
        raise SeedError(f"Seed booking id {booking_id!r} for {owner_id!r} must be a string.")

    return Booking(id=booking_id, start=start, end=start + SLOT_DURATION, visitor_name=visitor_name)


def _resolve_instant(now: datetime, day_offset: int, time_str: object, owner_id: str) -> datetime:
    if not isinstance(time_str, str):
        raise SeedError(f"Seed time {time_str!r} for {owner_id!r} must be an 'HH:MM' string.")
    try:
        hour_str, minute_str = time_str.split(":")
        hour, minute = int(hour_str), int(minute_str)
    except ValueError as exc:
        raise SeedError(f"Seed time {time_str!r} for {owner_id!r} is not 'HH:MM'.") from exc

    target_date: date = now.date() + timedelta(days=day_offset)
    instant = datetime(
        target_date.year, target_date.month, target_date.day, hour, minute, tzinfo=UTC
    )
    if not is_on_slot_boundary(instant):
        raise SeedError(
            f"Seed time {time_str!r} for {owner_id!r} must fall on a 30-minute boundary."
        )
    return instant
