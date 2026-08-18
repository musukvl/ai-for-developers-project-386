"""Thread-safe in-memory storage for calendars and bookings."""

from datetime import datetime
from threading import RLock
from uuid import uuid4

from .models import Booking, Calendar
from .slots import is_past


class StorageError(Exception):
    """Base class for storage-operation failures."""


class MissingResource(StorageError):
    """Raised when a requested active resource is not present."""


class StateConflict(StorageError):
    """Raised when a state transition is not possible."""


class CalendarStore:
    """Own all mutable application data behind a process-wide reentrant lock."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._users: set[str] = set()
        self._calendars: dict[str, Calendar] = {}

    def register_user(self, name: str) -> bool:
        """Register a user and return whether this was their first appearance."""
        with self._lock:
            is_new = name not in self._users
            self._users.add(name)
            return is_new

    def has_calendar(self, owner_id: str) -> bool:
        """Return whether the user owns a calendar."""
        with self._lock:
            return owner_id in self._calendars

    def create_calendar(self, owner_id: str) -> Calendar:
        """Create the one permitted public calendar for the owner."""
        with self._lock:
            if owner_id in self._calendars:
                raise StateConflict("This user already has a calendar.")
            self._users.add(owner_id)
            calendar = Calendar(owner_id=owner_id)
            self._calendars[owner_id] = calendar
            return calendar

    def calendar_for(self, owner_id: str) -> Calendar:
        """Return a calendar regardless of active slots."""
        with self._lock:
            try:
                return self._calendars[owner_id]
            except KeyError as error:
                raise MissingResource("Calendar not found.") from error

    def add_slots(self, owner_id: str, starts: list[datetime]) -> Calendar:
        """Add slots idempotently without affecting bookings."""
        with self._lock:
            calendar = self.calendar_for(owner_id)
            calendar.slots.update(starts)
            return calendar

    def remove_slot(self, owner_id: str, start: datetime, now: datetime) -> None:
        """Remove one currently free slot."""
        with self._lock:
            calendar = self.calendar_for(owner_id)
            if is_past(start, now) or start not in calendar.slots:
                raise MissingResource("Available slot not found.")
            if any(booking.start == start for booking in calendar.bookings.values()):
                raise StateConflict("The slot is booked; cancel the booking first.")
            calendar.slots.remove(start)

    def create_booking(
        self, owner_id: str, start: datetime, visitor_name: str, now: datetime
    ) -> Booking:
        """Atomically check availability and reserve a slot."""
        with self._lock:
            calendar = self.calendar_for(owner_id)
            if is_past(start, now):
                raise StateConflict("The slot has already started.")
            if start not in calendar.slots:
                if any(booking.start == start for booking in calendar.bookings.values()):
                    raise StateConflict("The slot was already taken.")
                raise StateConflict("The slot is not available.")
            if any(booking.start == start for booking in calendar.bookings.values()):
                raise StateConflict("The slot was already taken.")
            booking = Booking(id=uuid4().hex, start=start, visitor_name=visitor_name)
            calendar.bookings[booking.id] = booking
            return booking

    def add_seed_booking(self, owner_id: str, booking: Booking) -> None:
        """Load a prevalidated booking without changing its readable ID."""
        with self._lock:
            calendar = self.calendar_for(owner_id)
            calendar.bookings[booking.id] = booking

    def cancel_booking(
        self, owner_id: str, booking_id: str, now: datetime, visitor_name: str | None = None
    ) -> Booking:
        """Cancel an active booking, optionally requiring its visitor to match."""
        with self._lock:
            calendar = self.calendar_for(owner_id)
            booking = calendar.bookings.get(booking_id)
            if booking is None or is_past(booking.start, now):
                raise MissingResource("Booking not found.")
            if visitor_name is not None and booking.visitor_name != visitor_name:
                raise MissingResource("Booking not found.")
            del calendar.bookings[booking_id]
            return booking

    def active_slots(self, owner_id: str, now: datetime) -> list[datetime]:
        """List visible, unbooked slots in ascending order."""
        with self._lock:
            calendar = self.calendar_for(owner_id)
            booked_starts = {booking.start for booking in calendar.bookings.values()}
            return sorted(
                start
                for start in calendar.slots
                if not is_past(start, now) and start not in booked_starts
            )

    def active_bookings(
        self, owner_id: str, now: datetime, visitor_name: str | None = None
    ) -> list[Booking]:
        """List visible bookings sorted by start then ID."""
        with self._lock:
            calendar = self.calendar_for(owner_id)
            return sorted(
                (
                    booking
                    for booking in calendar.bookings.values()
                    if not is_past(booking.start, now)
                    and (visitor_name is None or booking.visitor_name == visitor_name)
                ),
                key=lambda booking: (booking.start, booking.id),
            )
