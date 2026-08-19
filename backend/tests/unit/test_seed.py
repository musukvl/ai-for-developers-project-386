"""Unit tests for seed loading: relative-day expansion and validation."""

from datetime import UTC, datetime, timedelta

import pytest
import yaml

from src.seed import SeedError, load_seed
from src.storage import Storage

UTC = UTC
NOW = datetime(2026, 8, 1, 0, 0, 0, tzinfo=UTC)


def _write_seed(tmp_path, data: dict) -> str:
    path = tmp_path / "seed.yml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return str(path)


class TestRelativeDayExpansion:
    def test_day_zero_is_today(self, tmp_path):
        seed_file = _write_seed(
            tmp_path,
            {
                "users": ["alex"],
                "calendars": [
                    {
                        "ownerId": "alex",
                        "availability": [{"day": 0, "start": "10:00", "end": "11:00"}],
                    }
                ],
            },
        )
        storage = Storage()
        load_seed(storage, seed_file, now=NOW)

        slots = storage.get_available_slots("alex", NOW)
        assert [s.start for s in slots] == [
            NOW + timedelta(hours=10),
            NOW + timedelta(hours=10, minutes=30),
        ]

    def test_positive_day_offset(self, tmp_path):
        seed_file = _write_seed(
            tmp_path,
            {
                "users": ["alex"],
                "calendars": [
                    {
                        "ownerId": "alex",
                        "availability": [{"day": 2, "start": "10:00", "end": "10:30"}],
                    }
                ],
            },
        )
        storage = Storage()
        load_seed(storage, seed_file, now=NOW)

        slots = storage.get_available_slots("alex", NOW)
        assert slots[0].start == NOW + timedelta(days=2, hours=10)

    def test_negative_day_offset_is_stored_but_invisible(self, tmp_path):
        seed_file = _write_seed(
            tmp_path,
            {
                "users": ["alex", "sam"],
                "calendars": [
                    {
                        "ownerId": "alex",
                        "availability": [{"day": -1, "start": "10:00", "end": "11:00"}],
                        "bookings": [
                            {
                                "id": "past-booking",
                                "day": -1,
                                "start": "10:00",
                                "visitorName": "sam",
                            }
                        ],
                    }
                ],
            },
        )
        storage = Storage()
        load_seed(storage, seed_file, now=NOW)

        assert storage.get_available_slots("alex", NOW) == []
        assert storage.get_bookings("alex", NOW) == []

    def test_bookings_remove_slot_from_available_list(self, tmp_path):
        seed_file = _write_seed(
            tmp_path,
            {
                "users": ["alex", "sam"],
                "calendars": [
                    {
                        "ownerId": "alex",
                        "availability": [{"day": 1, "start": "10:00", "end": "11:00"}],
                        "bookings": [{"day": 1, "start": "10:00", "visitorName": "sam"}],
                    }
                ],
            },
        )
        storage = Storage()
        load_seed(storage, seed_file, now=NOW)

        available_starts = {s.start for s in storage.get_available_slots("alex", NOW)}
        assert (NOW + timedelta(days=1, hours=10)) not in available_starts
        assert (NOW + timedelta(days=1, hours=10, minutes=30)) in available_starts

        bookings = storage.get_bookings("alex", NOW)
        assert len(bookings) == 1
        assert bookings[0].visitor_name == "sam"


class TestSeedValidation:
    def test_invalid_user_name_aborts(self, tmp_path):
        seed_file = _write_seed(tmp_path, {"users": ["Sam"], "calendars": []})
        with pytest.raises(SeedError):
            load_seed(Storage(), seed_file, now=NOW)

    def test_unknown_owner_aborts(self, tmp_path):
        seed_file = _write_seed(
            tmp_path, {"users": ["alex"], "calendars": [{"ownerId": "sam", "availability": []}]}
        )
        with pytest.raises(SeedError):
            load_seed(Storage(), seed_file, now=NOW)

    def test_booking_off_published_slot_aborts(self, tmp_path):
        seed_file = _write_seed(
            tmp_path,
            {
                "users": ["alex", "sam"],
                "calendars": [
                    {
                        "ownerId": "alex",
                        "availability": [{"day": 1, "start": "10:00", "end": "10:30"}],
                        "bookings": [{"day": 1, "start": "11:00", "visitorName": "sam"}],
                    }
                ],
            },
        )
        with pytest.raises(SeedError):
            load_seed(Storage(), seed_file, now=NOW)

    def test_booking_with_unknown_visitor_aborts(self, tmp_path):
        seed_file = _write_seed(
            tmp_path,
            {
                "users": ["alex"],
                "calendars": [
                    {
                        "ownerId": "alex",
                        "availability": [{"day": 1, "start": "10:00", "end": "10:30"}],
                        "bookings": [{"day": 1, "start": "10:00", "visitorName": "ghost"}],
                    }
                ],
            },
        )
        with pytest.raises(SeedError):
            load_seed(Storage(), seed_file, now=NOW)

    def test_off_boundary_time_aborts(self, tmp_path):
        seed_file = _write_seed(
            tmp_path,
            {
                "users": ["alex"],
                "calendars": [
                    {
                        "ownerId": "alex",
                        "availability": [{"day": 1, "start": "10:15", "end": "11:00"}],
                    }
                ],
            },
        )
        with pytest.raises(SeedError):
            load_seed(Storage(), seed_file, now=NOW)

    def test_second_calendar_for_same_owner_aborts(self, tmp_path):
        seed_file = _write_seed(
            tmp_path,
            {
                "users": ["alex"],
                "calendars": [
                    {"ownerId": "alex", "availability": []},
                    {"ownerId": "alex", "availability": []},
                ],
            },
        )
        with pytest.raises(SeedError):
            load_seed(Storage(), seed_file, now=NOW)

    def test_malformed_yaml_aborts(self, tmp_path):
        path = tmp_path / "broken.yml"
        path.write_text("users: [alex\n", encoding="utf-8")
        with pytest.raises(SeedError):
            load_seed(Storage(), str(path), now=NOW)

    def test_missing_file_aborts(self, tmp_path):
        with pytest.raises(SeedError):
            load_seed(Storage(), str(tmp_path / "does-not-exist.yml"), now=NOW)

    def test_empty_seed_file_is_allowed(self, tmp_path):
        path = tmp_path / "empty.yml"
        path.write_text("", encoding="utf-8")
        load_seed(Storage(), str(path), now=NOW)
