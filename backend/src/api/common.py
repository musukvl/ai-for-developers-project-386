"""Shared HTTP request helpers, not role-specific API behavior."""

from datetime import UTC, datetime
from typing import ParamSpec, TypeVar

from flask import current_app, request

from ..errors import ApiError
from ..names import is_valid_name, normalize_name
from ..slots import format_timestamp
from ..storage import CalendarStore, MissingResource

Parameters = ParamSpec("Parameters")
ReturnValue = TypeVar("ReturnValue")


def store() -> CalendarStore:
    """Get the configured application store."""
    return current_app.extensions["calendar_store"]


def utc_now() -> datetime:
    """Return the time used for current-request visibility."""
    return datetime.now(UTC)


def require_user() -> str:
    """Validate, normalize, and auto-register the caller's header identity."""
    value = request.headers.get("X-User-Name")
    if value is None:
        raise ApiError("validation_error", "X-User-Name header is required.", 400)
    name = normalize_name(value)
    if not is_valid_name(name):
        raise ApiError("validation_error", "X-User-Name must be a valid user name.", 400)
    store().register_user(name)
    return name


def require_owner(owner_id: str) -> str:
    """Apply header validation then owner equality in the required order."""
    user = require_user()
    if user != owner_id:
        raise ApiError("name_mismatch", "X-User-Name must match the calendar owner.", 400)
    return user


def require_calendar(owner_id: str) -> None:
    """Ensure a conforming public calendar identifier exists."""
    if not is_valid_name(owner_id):
        raise ApiError("not_found", "Calendar not found.", 404)
    try:
        store().calendar_for(owner_id)
    except MissingResource as error:
        raise ApiError("not_found", str(error), 404) from error


def json_object() -> dict[str, object]:
    """Return an object JSON body or raise the documented validation error."""
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        raise ApiError("validation_error", "Request body must be a JSON object.", 400)
    return value


def slot_payload(start: datetime) -> dict[str, str]:
    """Serialize one fixed-duration slot."""
    from ..slots import SLOT_DURATION

    return {"start": format_timestamp(start), "end": format_timestamp(start + SLOT_DURATION)}


def booking_payload(booking) -> dict[str, str]:
    """Serialize a booking for the owning caller or booking visitor."""
    from ..slots import SLOT_DURATION

    return {
        "id": booking.id,
        "start": format_timestamp(booking.start),
        "end": format_timestamp(booking.start + SLOT_DURATION),
        "visitorName": booking.visitor_name,
    }
