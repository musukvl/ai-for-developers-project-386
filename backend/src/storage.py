"""Thread-safe in-memory store for event types and bookings.

Slots are not stored. They are generated from event-type duration and the
current occupancy on every read or booking attempt.
"""

from __future__ import annotations

import threading
from datetime import datetime

from src.domain import (
    Booking,
    EventType,
    Slot,
    classify_booking_slot,
    generate_booking_id,
    generate_slots,
    is_visible,
)


class EventTypeExistsError(Exception):
    """Raised when creating an event type whose id is already in use."""


class EventTypeNotFoundError(Exception):
    """Raised when the named event type does not exist."""


class FutureBookingsExistError(Exception):
    """Raised when deleting an event type that still has upcoming bookings."""


class BookingNotFoundError(Exception):
    """Raised when the named booking does not exist or has already started."""


class SlotConflictError(Exception):
    """Raised when a booking request fails a 409 occupancy/window/grid check."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class Storage:
    """In-memory dictionaries of event types and bookings, guarded by a lock."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._event_types: dict[str, EventType] = {}
        self._bookings: dict[str, Booking] = {}
        self.owner: str = "demo-owner"

    def list_event_types(self) -> list[EventType]:
        """Return all event types sorted by id."""
        with self._lock:
            return sorted(self._event_types.values(), key=lambda item: item.id)

    def get_event_type(self, event_type_id: str) -> EventType | None:
        """Return the event type or None when it does not exist."""
        with self._lock:
            return self._event_types.get(event_type_id)

    def create_event_type(self, event_type: EventType) -> EventType:
        """Insert an event type. Raises EventTypeExistsError on duplicate id."""
        with self._lock:
            if event_type.id in self._event_types:
                raise EventTypeExistsError(event_type.id)
            self._event_types[event_type.id] = event_type
            return event_type

    def delete_event_type(self, event_type_id: str, now: datetime) -> None:
        """Delete an event type unless upcoming bookings still reference it."""
        with self._lock:
            if event_type_id not in self._event_types:
                raise EventTypeNotFoundError(event_type_id)
            if any(
                booking.event_type_id == event_type_id and is_visible(booking.start, now)
                for booking in self._bookings.values()
            ):
                raise FutureBookingsExistError(event_type_id)
            del self._event_types[event_type_id]

    def list_upcoming_bookings(self, now: datetime) -> list[Booking]:
        """Return visible bookings sorted by start, then id."""
        with self._lock:
            visible = [
                booking for booking in self._bookings.values() if is_visible(booking.start, now)
            ]
            return sorted(visible, key=lambda booking: (booking.start, booking.id))

    def list_available_slots(self, event_type_id: str, now: datetime) -> list[Slot] | None:
        """Return generated free slots for an event type, or None if it is unknown."""
        with self._lock:
            event_type = self._event_types.get(event_type_id)
            if event_type is None:
                return None
            occupied = [(booking.start, booking.end) for booking in self._bookings.values()]
            return generate_slots(event_type.duration_minutes, now, occupied)

    def create_booking(
        self,
        event_type_id: str,
        slot_start: datetime,
        guest_name: str,
        now: datetime,
        booking_id: str | None = None,
    ) -> Booking:
        """Reserve a generated slot atomically. Raises typed errors on failure."""
        with self._lock:
            event_type = self._event_types.get(event_type_id)
            if event_type is None:
                raise EventTypeNotFoundError(event_type_id)

            existing = list(self._bookings.values())
            decision = classify_booking_slot(event_type, slot_start, existing, now)
            if isinstance(decision, str):
                raise SlotConflictError(decision)

            booking = Booking(
                id=booking_id or generate_booking_id(),
                event_type_id=event_type.id,
                event_type_title=event_type.title,
                start=decision.start,
                end=decision.end,
                guest_name=guest_name,
            )
            self._bookings[booking.id] = booking
            return booking

    def seed_booking(self, booking: Booking) -> None:
        """Insert a pre-validated booking from seed data without window checks."""
        with self._lock:
            self._bookings[booking.id] = booking

    def cancel_booking(self, booking_id: str, now: datetime) -> None:
        """Remove an upcoming booking. Past or unknown ids look like not-found."""
        with self._lock:
            booking = self._bookings.get(booking_id)
            if booking is None or not is_visible(booking.start, now):
                raise BookingNotFoundError(booking_id)
            del self._bookings[booking_id]
