"""In-memory storage: users, calendars, availability, and bookings.

Every mutation and every read that must reflect "now" is guarded by one
process-wide `threading.RLock`, which is what makes the booking
check-and-reserve atomic. Nothing here persists across a restart; seed data
is reloaded into a fresh instance every time the app starts.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime

from src.domain import Booking, Slot, is_visible


class CalendarExistsError(Exception):
    """Raised when a user already owns a calendar."""


class CalendarNotFoundError(Exception):
    """Raised when the calendar named in a request does not exist or is unreachable."""


class SlotNotFoundError(Exception):
    """Raised when no available slot starts at the requested instant."""


class SlotBookedError(Exception):
    """Raised when a removal targets a slot that is currently booked."""


class SlotUnavailableError(Exception):
    """Raised when a booking attempt targets a slot that cannot be booked."""


class BookingNotFoundError(Exception):
    """Raised when the booking named in a request does not exist or is unreachable."""


@dataclass
class Calendar:
    """One owner's calendar: available slots keyed by start, plus confirmed bookings."""

    owner_id: str
    slots: dict[datetime, Slot] = field(default_factory=dict)
    bookings: dict[str, Booking] = field(default_factory=dict)


class Storage:
    """Thread-safe in-memory store for users and calendars."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._users: set[str] = set()
        self._calendars: dict[str, Calendar] = {}

    def register_user(self, name: str) -> bool:
        """Register a name if unknown. Returns True when it was newly registered."""
        with self._lock:
            if name in self._users:
                return False
            self._users.add(name)
            return True

    def has_user(self, name: str) -> bool:
        with self._lock:
            return name in self._users

    def has_calendar(self, owner_id: str) -> bool:
        with self._lock:
            return owner_id in self._calendars

    def list_calendar_owner_ids(self) -> list[str]:
        """Return all calendar owner IDs in ascending alphabetical order."""
        with self._lock:
            return sorted(self._calendars)

    def create_calendar(self, owner_id: str) -> None:
        """Create an empty public calendar for `owner_id`."""
        with self._lock:
            if owner_id in self._calendars:
                raise CalendarExistsError(owner_id)
            self._calendars[owner_id] = Calendar(owner_id=owner_id)

    def seed_calendar(self, owner_id: str, slots: list[Slot], bookings: list[Booking]) -> None:
        """Directly populate a freshly created calendar's slots and bookings from seed data."""
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                raise CalendarNotFoundError(owner_id)
            for slot in slots:
                calendar.slots[slot.start] = slot
            for booking in bookings:
                calendar.bookings[booking.id] = booking

    def get_available_slots(self, owner_id: str, now: datetime) -> list[Slot] | None:
        """Return the calendar's visible available slots, sorted ascending by start."""
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                return None
            visible = [slot for slot in calendar.slots.values() if is_visible(slot.start, now)]
            return sorted(visible, key=lambda slot: slot.start)

    def get_bookings(self, owner_id: str, now: datetime) -> list[Booking] | None:
        """Return all visible bookings for the calendar, sorted by start then id."""
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                return None
            visible = [
                booking for booking in calendar.bookings.values() if is_visible(booking.start, now)
            ]
            return sorted(visible, key=lambda booking: (booking.start, booking.id))

    def get_my_bookings(
        self, owner_id: str, visitor_name: str, now: datetime
    ) -> list[Booking] | None:
        """Return the visible bookings made by `visitor_name`, sorted by start then id."""
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                return None
            mine = [
                booking
                for booking in calendar.bookings.values()
                if booking.visitor_name == visitor_name and is_visible(booking.start, now)
            ]
            return sorted(mine, key=lambda booking: (booking.start, booking.id))

    def add_availability(
        self, owner_id: str, new_slots: list[Slot], now: datetime
    ) -> list[Slot]:
        """Merge new slots into the calendar and return the resulting visible available slots.

        Slots already present (available or booked) are retained once; a
        booked slot's availability entry is never re-added.
        """
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                raise CalendarNotFoundError(owner_id)
            booked_starts = {booking.start for booking in calendar.bookings.values()}
            for slot in new_slots:
                if slot.start in booked_starts:
                    continue
                calendar.slots.setdefault(slot.start, slot)
            visible = [s for s in calendar.slots.values() if is_visible(s.start, now)]
            return sorted(visible, key=lambda slot: slot.start)

    def remove_available_slot(self, owner_id: str, slot_start: datetime, now: datetime) -> None:
        """Remove a single available slot. Raises if the calendar/slot is missing or booked."""
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                raise CalendarNotFoundError(owner_id)
            if any(
                booking.start == slot_start and is_visible(booking.start, now)
                for booking in calendar.bookings.values()
            ):
                raise SlotBookedError(slot_start)
            slot = calendar.slots.get(slot_start)
            if slot is None or not is_visible(slot.start, now):
                raise SlotNotFoundError(slot_start)
            del calendar.slots[slot_start]

    def create_booking(
        self, owner_id: str, slot_start: datetime, visitor_name: str, booking_id: str, now: datetime
    ) -> Booking:
        """Atomically reserve an available slot for `visitor_name`."""
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                raise CalendarNotFoundError(owner_id)
            slot = calendar.slots.get(slot_start)
            if slot is None or not is_visible(slot.start, now):
                raise SlotUnavailableError(slot_start)
            del calendar.slots[slot_start]
            booking = Booking(
                id=booking_id, start=slot.start, end=slot.end, visitor_name=visitor_name
            )
            calendar.bookings[booking.id] = booking
            return booking

    def cancel_booking_as_owner(self, owner_id: str, booking_id: str, now: datetime) -> None:
        """Cancel any booking on the calendar and return its slot to availability."""
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                raise CalendarNotFoundError(owner_id)
            booking = calendar.bookings.get(booking_id)
            if booking is None or not is_visible(booking.start, now):
                raise BookingNotFoundError(booking_id)
            del calendar.bookings[booking_id]
            calendar.slots[booking.start] = Slot(start=booking.start, end=booking.end)

    def cancel_booking_as_visitor(
        self, owner_id: str, booking_id: str, visitor_name: str, now: datetime
    ) -> None:
        """Cancel the caller's own booking. Another user's booking looks like not-found."""
        with self._lock:
            calendar = self._calendars.get(owner_id)
            if calendar is None:
                raise CalendarNotFoundError(owner_id)
            booking = calendar.bookings.get(booking_id)
            if (
                booking is None
                or booking.visitor_name != visitor_name
                or not is_visible(booking.start, now)
            ):
                raise BookingNotFoundError(booking_id)
            del calendar.bookings[booking_id]
            calendar.slots[booking.start] = Slot(start=booking.start, end=booking.end)
