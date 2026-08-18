"""In-memory domain data structures."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Booking:
    """A reservation of a calendar slot by a visitor."""

    id: str
    start: datetime
    visitor_name: str


@dataclass
class Calendar:
    """One owner's public availability and bookings."""

    owner_id: str
    slots: set[datetime] = field(default_factory=set)
    bookings: dict[str, Booking] = field(default_factory=dict)


@dataclass(frozen=True)
class User:
    """A normalized user identity."""

    name: str
