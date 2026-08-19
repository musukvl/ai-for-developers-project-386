"""Role-neutral calendar existence check, shared by both owner and visitor routes.

This is not owner or visitor logic; it only decides whether `{ownerId}` in a
path names a real calendar, per the fixed check order in spec/api.md.
"""

from __future__ import annotations

from src.domain import is_valid_name
from src.errors import not_found
from src.storage import Storage


def ensure_calendar_exists(storage: Storage, owner_id: str) -> None:
    """Raise `not_found` unless `owner_id` is a conforming name with an existing calendar.

    A path `{ownerId}` that is not a valid normalized name can never have a
    calendar, so it is reported the same way as a missing one.
    """
    if not is_valid_name(owner_id) or not storage.has_calendar(owner_id):
        raise not_found("Calendar not found.")
