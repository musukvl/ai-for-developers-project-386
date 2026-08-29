"""Unit tests for slot generation, the 14-day window, and occupancy."""

from datetime import UTC, datetime, timedelta

from src.domain import (
    WINDOW_DAYS,
    Booking,
    EventType,
    classify_booking_slot,
    generate_slots,
    is_on_duration_grid,
    is_within_window,
    slot_end,
    window_last_date,
)

THIRTY = EventType(
    id="thirty-minute-call",
    title="30m call",
    description="A standard call.",
    duration_minutes=30,
)
FIFTEEN = EventType(
    id="fifteen-minute-call",
    title="15m call",
    description="A short call.",
    duration_minutes=15,
)

# Fixed instant so grid and window tests do not depend on wall-clock time.
NOW = datetime(2026, 8, 1, 9, 12, tzinfo=UTC)


def _start_on(day_offset: int, hour: int, minute: int) -> datetime:
    day = NOW.date() + timedelta(days=day_offset)
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=UTC)


class TestDurationGrid:
    def test_30m_starts_on_the_hour_and_half_hour(self):
        assert is_on_duration_grid(_start_on(1, 10, 0), 30) is True
        assert is_on_duration_grid(_start_on(1, 10, 30), 30) is True

    def test_30m_rejects_off_grid_minutes(self):
        assert is_on_duration_grid(_start_on(1, 10, 17), 30) is False

    def test_30m_last_same_day_start_is_23_00(self):
        assert is_on_duration_grid(_start_on(1, 23, 0), 30) is True
        assert is_on_duration_grid(_start_on(1, 23, 30), 30) is False

    def test_15m_last_same_day_start_is_23_30(self):
        assert is_on_duration_grid(_start_on(1, 23, 30), 15) is True
        assert is_on_duration_grid(_start_on(1, 23, 45), 15) is False


class TestWindow:
    def test_window_covers_today_through_today_plus_13(self):
        assert WINDOW_DAYS == 14
        assert window_last_date(NOW) == NOW.date() + timedelta(days=13)

    def test_today_plus_13_is_inside_window(self):
        start = _start_on(13, 10, 0)
        assert is_within_window(start, NOW) is True

    def test_day_14_is_outside_window(self):
        start = _start_on(14, 10, 0)
        assert is_within_window(start, NOW) is False

    def test_past_start_is_outside_window(self):
        start = NOW - timedelta(minutes=30)
        assert is_within_window(start, NOW) is False


class TestGenerateSlots:
    def test_skips_starts_that_have_already_passed(self):
        slots = generate_slots(30, NOW, occupied=[])
        assert all(slot.start >= NOW for slot in slots)
        assert slots[0].start == datetime(2026, 8, 1, 9, 30, tzinfo=UTC)

    def test_30m_slots_are_consecutive_and_same_day(self):
        noon = datetime(2026, 8, 2, 0, 0, tzinfo=UTC)
        slots = generate_slots(30, noon, occupied=[])
        first_day = [slot for slot in slots if slot.start.date() == noon.date()]
        assert first_day[0].start.hour == 0
        assert first_day[0].start.minute == 0
        assert first_day[-1].start == datetime(2026, 8, 2, 23, 0, tzinfo=UTC)
        assert first_day[-1].end == datetime(2026, 8, 2, 23, 30, tzinfo=UTC)
        assert all(slot.end.date() == slot.start.date() for slot in first_day)

    def test_occupied_interval_is_subtracted_for_every_duration(self):
        occupied_start = _start_on(1, 10, 0)
        occupied = [(occupied_start, slot_end(occupied_start, 30))]
        thirty = generate_slots(30, NOW, occupied)
        fifteen = generate_slots(15, NOW, occupied)
        assert all(slot.start != occupied_start for slot in thirty)
        occupied_end = occupied_start + timedelta(minutes=30)
        assert all(
            not (slot.start >= occupied_start and slot.start < occupied_end)
            for slot in fifteen
        )


class TestClassifyBooking:
    def test_overlap_is_occupied_even_across_event_types(self):
        existing = [
            Booking(
                id="seed-1",
                event_type_id=THIRTY.id,
                event_type_title=THIRTY.title,
                start=_start_on(1, 10, 0),
                end=_start_on(1, 10, 30),
                guest_name="Sam",
            )
        ]
        decision = classify_booking_slot(FIFTEEN, _start_on(1, 10, 15), existing, NOW)
        assert decision == "slot_occupied"

    def test_day_14_is_outside_window(self):
        decision = classify_booking_slot(THIRTY, _start_on(14, 10, 0), [], NOW)
        assert decision == "slot_outside_window"

    def test_off_grid_inside_window_is_mismatch(self):
        decision = classify_booking_slot(THIRTY, _start_on(1, 10, 17), [], NOW)
        assert decision == "slot_mismatch"

    def test_free_on_grid_slot_is_accepted(self):
        start = _start_on(1, 10, 0)
        decision = classify_booking_slot(THIRTY, start, [], NOW)
        assert decision.start == start
        assert decision.end == slot_end(start, 30)
