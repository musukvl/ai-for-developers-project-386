"""Calendar-owner API contract."""

from flask import Blueprint, jsonify

from ..errors import ApiError
from ..logging_setup import log_event
from ..slots import expand_range, format_timestamp, parse_timestamp, validate_horizon
from ..storage import MissingResource, StateConflict
from .common import (
    booking_payload,
    json_object,
    require_calendar,
    require_owner,
    slot_payload,
    store,
    utc_now,
)

blueprint = Blueprint("owner", __name__, url_prefix="/api")


@blueprint.post("/calendars")
def create_calendar() -> tuple[object, int]:
    """Create a user's single public calendar."""
    user = require_owner_body()
    try:
        store().create_calendar(user)
    except StateConflict as error:
        raise ApiError("conflict", str(error), 409) from error
    log_event("calendar.created", owner_id=user, user=user)
    return jsonify(ownerId=user, calendarUrl=f"/cal/{user}"), 201


@blueprint.get("/calendars/<owner_id>/owner")
def get_owner_calendar(owner_id: str) -> tuple[object, int]:
    """Return the owner-only calendar representation."""
    require_owner(owner_id)
    require_calendar(owner_id)
    return jsonify(_owner_payload(owner_id)), 200


@blueprint.post("/calendars/<owner_id>/availability")
def add_availability(owner_id: str) -> tuple[object, int]:
    """Expand and publish an owner availability range."""
    require_owner(owner_id)
    require_calendar(owner_id)
    body = json_object()
    now = utc_now()
    try:
        start = parse_timestamp(body.get("start"))
        end = parse_timestamp(body.get("end"))
        starts = expand_range(start, end)
        validate_horizon(start, end, now)
    except ValueError as error:
        raise ApiError("validation_error", str(error), 400) from error
    store().add_slots(owner_id, starts)
    log_event("availability.added", owner_id=owner_id, slot_count=len(starts))
    return jsonify(
        availableSlots=[slot_payload(start) for start in store().active_slots(owner_id, now)]
    ), 200


@blueprint.delete("/calendars/<owner_id>/availability/<path:slot_start>")
def remove_availability(owner_id: str, slot_start: str) -> tuple[str, int]:
    """Remove one available calendar slot."""
    require_owner(owner_id)
    require_calendar(owner_id)
    now = utc_now()
    try:
        start = parse_timestamp(slot_start)
        store().remove_slot(owner_id, start, now)
    except ValueError as error:
        raise ApiError("not_found", "Available slot not found.", 404) from error
    except MissingResource as error:
        raise ApiError("not_found", str(error), 404) from error
    except StateConflict as error:
        raise ApiError("conflict", str(error), 409) from error
    log_event("slot.removed", owner_id=owner_id, slot_start=format_timestamp(start))
    return "", 204


@blueprint.delete("/calendars/<owner_id>/owner/bookings/<booking_id>")
def cancel_booking(owner_id: str, booking_id: str) -> tuple[str, int]:
    """Cancel any active booking on the owner's calendar."""
    require_owner(owner_id)
    require_calendar(owner_id)
    try:
        store().cancel_booking(owner_id, booking_id, utc_now())
    except MissingResource as error:
        raise ApiError("not_found", str(error), 404) from error
    log_event("booking.cancelled", owner_id=owner_id, booking_id=booking_id)
    return "", 204


def require_owner_body() -> str:
    """Validate the header and ownerId body identity for calendar creation."""
    from .common import require_user

    user = require_user()
    body = json_object()
    owner_id = body.get("ownerId")
    if not isinstance(owner_id, str):
        raise ApiError("validation_error", "ownerId must be a string.", 400)
    if owner_id != user:
        raise ApiError("name_mismatch", "ownerId must match X-User-Name.", 400)
    return user


def _owner_payload(owner_id: str) -> dict[str, object]:
    now = utc_now()
    return {
        "ownerId": owner_id,
        "availableSlots": [slot_payload(start) for start in store().active_slots(owner_id, now)],
        "bookings": [
            booking_payload(booking) for booking in store().active_bookings(owner_id, now)
        ],
    }
