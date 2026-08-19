"""Unit tests for pure calculation logic: naming, timestamps, slots, horizon."""

from datetime import UTC, datetime, timedelta

import pytest

from src.domain import (
    HORIZON,
    SLOT_DURATION,
    Slot,
    expand_range_to_slots,
    format_utc_timestamp,
    generate_booking_id,
    horizon_end,
    is_on_slot_boundary,
    is_valid_name,
    is_visible,
    is_within_horizon,
    normalize_name,
    parse_utc_timestamp,
    validate_availability_range,
)

UTC = UTC


def _dt(*args) -> datetime:
    return datetime(*args, tzinfo=UTC)


class TestNormalizeName:
    def test_trims_and_lowercases(self):
        assert normalize_name("  Sam  ") == "sam"

    def test_only_trims_and_lowercases_no_other_rewrites(self):
        assert normalize_name("Sam Smith") == "sam smith"


class TestIsValidName:
    @pytest.mark.parametrize("name", ["sam", "sam-smith", "a1-2b", "a" * 64])
    def test_valid_names(self, name):
        assert is_valid_name(name) is True

    @pytest.mark.parametrize(
        "name",
        [
            "",
            "ab",  # too short
            "a" * 65,  # too long
            "Sam",  # uppercase
            "sam smith",  # space
            "sam_smith",  # underscore
            "sam!",  # punctuation
        ],
    )
    def test_invalid_names(self, name):
        assert is_valid_name(name) is False


class TestTimestamps:
    def test_parse_and_format_round_trip(self):
        parsed = parse_utc_timestamp("2026-08-01T10:00:00Z")
        assert parsed == _dt(2026, 8, 1, 10, 0, 0)
        assert format_utc_timestamp(parsed) == "2026-08-01T10:00:00Z"

    @pytest.mark.parametrize(
        "value",
        [
            None,
            123,
            "",
            "not-a-date",
            "2026-08-01 10:00:00",
            "2026-08-01T10:00:00",
            "2026-08-01T10:00:00+02:00",
        ],
    )
    def test_unparseable_values_return_none(self, value):
        assert parse_utc_timestamp(value) is None


class TestSlotBoundary:
    @pytest.mark.parametrize("minute", [0, 30])
    def test_on_boundary(self, minute):
        assert is_on_slot_boundary(_dt(2026, 8, 1, 10, minute, 0)) is True

    @pytest.mark.parametrize("instant", [_dt(2026, 8, 1, 10, 15, 0), _dt(2026, 8, 1, 10, 0, 1)])
    def test_off_boundary(self, instant):
        assert is_on_slot_boundary(instant) is False


class TestHorizon:
    def test_horizon_end_is_28_days_later(self):
        now = _dt(2026, 8, 1, 0, 0, 0)
        assert horizon_end(now) == now + timedelta(days=28)
        assert HORIZON == timedelta(days=28)

    def test_within_horizon_true_at_bounds(self):
        now = _dt(2026, 8, 1, 0, 0, 0)
        assert is_within_horizon(now, horizon_end(now), now) is True

    def test_within_horizon_false_past_end(self):
        now = _dt(2026, 8, 1, 0, 0, 0)
        assert is_within_horizon(now, horizon_end(now) + timedelta(minutes=30), now) is False


class TestIsVisible:
    def test_future_start_is_visible(self):
        now = _dt(2026, 8, 1, 10, 0, 0)
        assert is_visible(now + timedelta(minutes=30), now) is True

    def test_past_start_is_not_visible(self):
        now = _dt(2026, 8, 1, 10, 0, 0)
        assert is_visible(now - timedelta(minutes=30), now) is False

    def test_exactly_now_is_visible(self):
        now = _dt(2026, 8, 1, 10, 0, 0)
        assert is_visible(now, now) is True


class TestValidateAvailabilityRange:
    def test_valid_range(self):
        now = _dt(2026, 8, 1, 0, 0, 0)
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=1)
        assert validate_availability_range(start, end, now) is None

    def test_off_boundary_start(self):
        now = _dt(2026, 8, 1, 0, 0, 0)
        start = now + timedelta(minutes=15)
        end = start + timedelta(hours=1)
        assert validate_availability_range(start, end, now) is not None

    def test_end_not_after_start(self):
        now = _dt(2026, 8, 1, 0, 0, 0)
        start = now + timedelta(hours=1)
        assert validate_availability_range(start, start, now) is not None

    def test_end_before_start(self):
        now = _dt(2026, 8, 1, 0, 0, 0)
        start = now + timedelta(hours=1)
        end = start - timedelta(minutes=30)
        assert validate_availability_range(start, end, now) is not None

    def test_outside_horizon(self):
        now = _dt(2026, 8, 1, 0, 0, 0)
        start = horizon_end(now) + timedelta(minutes=30)
        end = start + timedelta(minutes=30)
        assert validate_availability_range(start, end, now) is not None

    def test_before_now_is_rejected_by_default(self):
        now = _dt(2026, 8, 1, 10, 0, 0)
        start = now - timedelta(hours=1)
        end = now - timedelta(minutes=30)
        assert validate_availability_range(start, end, now) is not None

    def test_before_now_is_allowed_with_allow_past(self):
        now = _dt(2026, 8, 1, 10, 0, 0)
        start = now - timedelta(hours=1)
        end = now - timedelta(minutes=30)
        assert validate_availability_range(start, end, now, allow_past=True) is None


class TestExpandRangeToSlots:
    def test_expands_into_30_minute_slots(self):
        start = _dt(2026, 8, 1, 10, 0, 0)
        end = start + timedelta(hours=1)
        slots = expand_range_to_slots(start, end)
        assert slots == [
            Slot(start=start, end=start + SLOT_DURATION),
            Slot(start=start + SLOT_DURATION, end=end),
        ]

    def test_empty_range_produces_no_slots(self):
        start = _dt(2026, 8, 1, 10, 0, 0)
        assert expand_range_to_slots(start, start) == []


class TestGenerateBookingId:
    def test_generates_unique_opaque_ids(self):
        first = generate_booking_id()
        second = generate_booking_id()
        assert first != second
        assert isinstance(first, str) and len(first) > 0
