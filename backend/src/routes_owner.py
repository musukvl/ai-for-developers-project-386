"""Owner API: create a calendar, manage its availability, and manage its bookings.

Owner and visitor logic never mix in one handler; the only thing shared with
the visitor module is storage and the neutral `calendar_lookup` helper.
"""

from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, current_app, jsonify, request

from src.auth import get_user_name, require_owner_match
from src.calendar_lookup import ensure_calendar_exists
from src.domain import expand_range_to_slots, parse_utc_timestamp, validate_availability_range
from src.errors import conflict, name_mismatch, not_found, validation_error
from src.logging_setup import logger
from src.serializers import serialize_owner_calendar, serialize_slot
from src.storage import BookingNotFoundError, SlotBookedError, SlotNotFoundError, Storage

owner_bp = Blueprint("owner", __name__)


@owner_bp.post("/api/calendars")
def create_calendar():
    storage: Storage = current_app.config["STORAGE"]
    user_name = get_user_name()

    body = request.get_json(silent=True)
    owner_id = body.get("ownerId") if isinstance(body, dict) else None
    if not isinstance(owner_id, str):
        raise validation_error("The 'ownerId' field is required.")
    if owner_id != user_name:
        raise name_mismatch()

    if storage.has_calendar(user_name):
        raise conflict("A calendar already exists for this user.")

    storage.create_calendar(user_name)
    logger.bind(event="calendar.created", owner_id=user_name).info("calendar.created")

    return jsonify({"ownerId": user_name, "calendarUrl": f"/cal/{user_name}"}), 201


@owner_bp.get("/api/calendars/<owner_id>/owner")
def get_owner_calendar(owner_id: str):
    storage: Storage = current_app.config["STORAGE"]
    user_name = get_user_name()
    require_owner_match(user_name, owner_id)
    ensure_calendar_exists(storage, owner_id)

    now = datetime.now(UTC)
    available_slots = storage.get_available_slots(owner_id, now)
    bookings = storage.get_bookings(owner_id, now)
    return jsonify(serialize_owner_calendar(owner_id, available_slots, bookings))


@owner_bp.post("/api/calendars/<owner_id>/availability")
def add_availability(owner_id: str):
    storage: Storage = current_app.config["STORAGE"]
    user_name = get_user_name()
    require_owner_match(user_name, owner_id)
    ensure_calendar_exists(storage, owner_id)

    now = datetime.now(UTC)
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise validation_error("Request body must be a JSON object.")

    start = parse_utc_timestamp(body.get("start"))
    end = parse_utc_timestamp(body.get("end"))
    if start is None or end is None:
        raise validation_error("The 'start' and 'end' fields must be UTC ISO 8601 timestamps.")

    error = validate_availability_range(start, end, now)
    if error is not None:
        raise validation_error(error)

    new_slots = expand_range_to_slots(start, end)
    available_slots = storage.add_availability(owner_id, new_slots, now)

    logger.bind(
        event="availability.added",
        owner_id=owner_id,
        slot_start=start.isoformat(),
        slot_end=end.isoformat(),
        slots_added=len(new_slots),
    ).info("availability.added")

    return jsonify({"availableSlots": [serialize_slot(slot) for slot in available_slots]})


@owner_bp.delete("/api/calendars/<owner_id>/availability/<slot_start>")
def remove_availability_slot(owner_id: str, slot_start: str):
    storage: Storage = current_app.config["STORAGE"]
    user_name = get_user_name()
    require_owner_match(user_name, owner_id)
    ensure_calendar_exists(storage, owner_id)

    now = datetime.now(UTC)
    parsed_start = parse_utc_timestamp(slot_start)
    if parsed_start is None:
        raise not_found("No slot starts at that instant.")

    try:
        storage.remove_available_slot(owner_id, parsed_start, now)
    except SlotNotFoundError as exc:
        raise not_found("No slot starts at that instant.") from exc
    except SlotBookedError as exc:
        raise conflict(
            "The slot is booked; cancel the booking before removing the slot."
        ) from exc

    logger.bind(
        event="slot.removed", owner_id=owner_id, slot_start=parsed_start.isoformat()
    ).info("slot.removed")

    return "", 204


@owner_bp.delete("/api/calendars/<owner_id>/owner/bookings/<booking_id>")
def cancel_booking_as_owner(owner_id: str, booking_id: str):
    storage: Storage = current_app.config["STORAGE"]
    user_name = get_user_name()
    require_owner_match(user_name, owner_id)
    ensure_calendar_exists(storage, owner_id)

    now = datetime.now(UTC)
    try:
        storage.cancel_booking_as_owner(owner_id, booking_id, now)
    except BookingNotFoundError as exc:
        raise not_found("Booking not found.") from exc

    logger.bind(
        event="booking.cancelled", owner_id=owner_id, booking_id=booking_id, cancelled_by="owner"
    ).info("booking.cancelled")

    return "", 204
