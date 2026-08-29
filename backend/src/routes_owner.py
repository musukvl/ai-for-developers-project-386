"""Owner API: event-type administration and upcoming meetings.

Uses the predefined owner profile. There is no sign-in header.
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from src.domain import EventType, utc_now
from src.errors import (
    conflict,
    future_bookings_exist_error,
    not_found,
    validation_error,
)
from src.logging_setup import logger
from src.serializers import serialize_booking, serialize_event_type
from src.storage import (
    BookingNotFoundError,
    EventTypeExistsError,
    EventTypeNotFoundError,
    FutureBookingsExistError,
    Storage,
)

owner_bp = Blueprint("owner", __name__, url_prefix="/api/owner")


@owner_bp.post("/event-types")
def create_event_type():
    """Create an event type. Duplicate ids return 409 conflict."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise validation_error("Request body must be a JSON object.")

    event_type_id = _required_non_empty_string(body, "id")
    title = _required_non_empty_string(body, "title")
    description = body.get("description")
    if not isinstance(description, str):
        raise validation_error("description is required.")

    duration = body.get("durationMinutes")
    if not isinstance(duration, int) or isinstance(duration, bool) or duration < 1:
        raise validation_error("durationMinutes must be an integer of at least 1.")

    storage: Storage = current_app.config["STORAGE"]
    event_type = EventType(
        id=event_type_id,
        title=title,
        description=description,
        duration_minutes=duration,
    )
    try:
        created = storage.create_event_type(event_type)
    except EventTypeExistsError as exc:
        raise conflict("An event type with this id already exists.") from exc

    logger.bind(event="event_type.created", event_type_id=created.id).info("event_type.created")
    return jsonify(serialize_event_type(created))


@owner_bp.delete("/event-types/<event_type_id>")
def delete_event_type(event_type_id: str):
    """Delete an event type. Fails when upcoming bookings still reference it."""
    storage: Storage = current_app.config["STORAGE"]
    try:
        storage.delete_event_type(event_type_id, utc_now())
    except EventTypeNotFoundError as exc:
        raise not_found("Event type not found.") from exc
    except FutureBookingsExistError as exc:
        raise future_bookings_exist_error() from exc

    logger.bind(event="event_type.deleted", event_type_id=event_type_id).info(
        "event_type.deleted"
    )
    return ("", 204)


@owner_bp.get("/bookings")
def list_owner_bookings():
    """Return upcoming bookings of every event type in one list."""
    storage: Storage = current_app.config["STORAGE"]
    bookings = [serialize_booking(item) for item in storage.list_upcoming_bookings(utc_now())]
    return jsonify({"bookings": bookings})


@owner_bp.delete("/bookings/<booking_id>")
def cancel_booking(booking_id: str):
    """Cancel an upcoming booking. The interval becomes a free generated slot."""
    storage: Storage = current_app.config["STORAGE"]
    try:
        storage.cancel_booking(booking_id, utc_now())
    except BookingNotFoundError as exc:
        raise not_found("Booking not found.") from exc

    logger.bind(event="booking.cancelled", booking_id=booking_id).info("booking.cancelled")
    return ("", 204)


def _required_non_empty_string(body: dict, key: str) -> str:
    value = body.get(key)
    if not isinstance(value, str) or not value.strip():
        raise validation_error(f"{key} is required.")
    return value.strip()
