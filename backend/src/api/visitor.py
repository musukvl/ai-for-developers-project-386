"""Calendar-visitor API contract."""

from flask import Blueprint, jsonify

from ..errors import ApiError
from ..logging_setup import log_event
from ..slots import format_timestamp, parse_timestamp
from ..storage import MissingResource, StateConflict
from .common import (
    booking_payload,
    json_object,
    require_calendar,
    require_user,
    slot_payload,
    store,
    utc_now,
)

blueprint = Blueprint("visitor", __name__, url_prefix="/api")


@blueprint.get("/calendars/<owner_id>")
def get_visitor_calendar(owner_id: str) -> tuple[object, int]:
    """Return public availability and only this visitor's bookings."""
    user = require_user()
    require_calendar(owner_id)
    return jsonify(_visitor_payload(owner_id, user)), 200


@blueprint.post("/calendars/<owner_id>/bookings")
def create_booking(owner_id: str) -> tuple[object, int]:
    """Reserve one currently available slot for the caller."""
    user = require_user()
    require_calendar(owner_id)
    body = json_object()
    try:
        start = parse_timestamp(body.get("slotStart"))
    except ValueError as error:
        raise ApiError("validation_error", str(error), 400) from error
    try:
        booking = store().create_booking(owner_id, start, user, utc_now())
    except StateConflict as error:
        raise ApiError("conflict", str(error), 409) from error
    log_event(
        "booking.created",
        owner_id=owner_id,
        visitor_name=user,
        booking_id=booking.id,
        slot_start=format_timestamp(booking.start),
    )
    return jsonify(booking_payload(booking)), 201


@blueprint.delete("/calendars/<owner_id>/bookings/<booking_id>")
def cancel_booking(owner_id: str, booking_id: str) -> tuple[str, int]:
    """Cancel the caller's own active booking."""
    user = require_user()
    require_calendar(owner_id)
    try:
        store().cancel_booking(owner_id, booking_id, utc_now(), visitor_name=user)
    except MissingResource as error:
        raise ApiError("not_found", str(error), 404) from error
    log_event("booking.cancelled", owner_id=owner_id, visitor_name=user, booking_id=booking_id)
    return "", 204


def _visitor_payload(owner_id: str, visitor_name: str) -> dict[str, object]:
    now = utc_now()
    return {
        "ownerId": owner_id,
        "availableSlots": [slot_payload(start) for start in store().active_slots(owner_id, now)],
        "myBookings": [
            booking_payload(booking)
            for booking in store().active_bookings(owner_id, now, visitor_name=visitor_name)
        ],
    }
