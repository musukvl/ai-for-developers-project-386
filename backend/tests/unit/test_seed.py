"""Unit tests for seed loading and relative day expansion."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.domain import EventType
from src.seed import SeedError, load_seed
from src.storage import Storage

NOW = datetime(2026, 8, 1, 9, 12, tzinfo=UTC)
_DEFAULT_SEED = Path(__file__).resolve().parents[2] / "src" / "seed.yml"


def _write(path: Path, contents: str) -> str:
    path.write_text(contents, encoding="utf-8")
    return str(path)


class TestLoadSeed:
    def test_expands_positive_day_offset_from_today(self, tmp_path: Path):
        seed_path = _write(
            tmp_path / "seed.yml",
            """
owner: demo-owner
eventTypes:
  - id: thirty-minute-call
    title: 30m call
    description: A standard call.
    durationMinutes: 30
bookings:
  - id: seed-booking-1
    eventTypeId: thirty-minute-call
    day: +1
    start: "10:30"
    guestName: Sam
""",
        )
        storage = Storage()
        load_seed(storage, seed_path, now=NOW)

        bookings = storage.list_upcoming_bookings(NOW)
        assert len(bookings) == 1
        expected_start = datetime(2026, 8, 2, 10, 30, tzinfo=UTC)
        assert bookings[0].start == expected_start
        assert bookings[0].guest_name == "Sam"
        assert bookings[0].event_type_title == "30m call"

    def test_negative_day_offset_is_loaded_but_not_visible(self, tmp_path: Path):
        seed_path = _write(
            tmp_path / "seed.yml",
            """
owner: demo-owner
eventTypes:
  - id: thirty-minute-call
    title: 30m call
    description: A standard call.
    durationMinutes: 30
bookings:
  - id: past-booking-1
    eventTypeId: thirty-minute-call
    day: -1
    start: "10:00"
    guestName: Past
""",
        )
        storage = Storage()
        load_seed(storage, seed_path, now=NOW)
        assert storage.list_upcoming_bookings(NOW) == []

    def test_overlapping_seed_bookings_abort(self, tmp_path: Path):
        seed_path = _write(
            tmp_path / "seed.yml",
            """
owner: demo-owner
eventTypes:
  - id: fifteen-minute-call
    title: 15m call
    description: A short call.
    durationMinutes: 15
  - id: thirty-minute-call
    title: 30m call
    description: A standard call.
    durationMinutes: 30
bookings:
  - id: first
    eventTypeId: thirty-minute-call
    day: +1
    start: "10:00"
    guestName: Sam
  - id: second
    eventTypeId: fifteen-minute-call
    day: +1
    start: "10:15"
    guestName: Alex
""",
        )
        storage = Storage()
        with pytest.raises(SeedError, match="overlaps"):
            load_seed(storage, seed_path, now=NOW)

    def test_unknown_event_type_aborts(self, tmp_path: Path):
        seed_path = _write(
            tmp_path / "seed.yml",
            """
owner: demo-owner
eventTypes:
  - id: thirty-minute-call
    title: 30m call
    description: A standard call.
    durationMinutes: 30
bookings:
  - eventTypeId: missing
    day: +1
    start: "10:00"
    guestName: Sam
""",
        )
        with pytest.raises(SeedError, match="unknown event type"):
            load_seed(Storage(), seed_path, now=NOW)

    def test_invalid_yaml_aborts(self, tmp_path: Path):
        seed_path = _write(tmp_path / "seed.yml", "owner: [unterminated\n")
        with pytest.raises(SeedError):
            load_seed(Storage(), seed_path, now=NOW)

    def test_missing_file_aborts(self, tmp_path: Path):
        with pytest.raises(SeedError, match="does not exist"):
            load_seed(Storage(), str(tmp_path / "missing.yml"), now=NOW)

    def test_default_event_types_match_spec(self):
        storage = Storage()
        load_seed(storage, str(_DEFAULT_SEED), now=NOW)
        ids = {item.id: item for item in storage.list_event_types()}
        assert ids["fifteen-minute-call"] == EventType(
            id="fifteen-minute-call",
            title="15m call",
            description="A short call.",
            duration_minutes=15,
        )
        assert ids["thirty-minute-call"].duration_minutes == 30
        upcoming = storage.list_upcoming_bookings(NOW)
        assert upcoming[0].id == "seed-booking-1"
        assert upcoming[0].start == datetime(2026, 8, 2, 10, 30, tzinfo=UTC)
