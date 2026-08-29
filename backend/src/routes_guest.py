"""Guest API: event-type catalog, generated slots, and booking creation."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from src.domain import parse_utc_timestamp, utc_now
from src.errors import (
    not_found,
    slot_mismatch_error,
    slot_occupied_error,
    slot_outside_window_error,
    validation_error,
)
from src.logging_setup import logger
from src.serializers import serialize_booking, serialize_event_type, serialize_slot
from src.storage import EventTypeNotFoundError, SlotConflictError, Storage

guest_bp = Blueprint("guest", __name__, url_prefix="/api")

_CONFLICT_ERRORS = {
    "slot_occupied": slot_occupied_error,
    "slot_outside_window": slot_outside_window_error,
    "slot_mismatch": slot_mismatch_error,
}


@guest_bp.get("/event-types")
def list_event_types():
    """Return the public event-type catalog. No login."""
    storage: Storage = current_app.config["STORAGE"]
    event_types = [serialize_event_type(item) for item in storage.list_event_types()]
    return jsonify({"eventTypes": event_types})


@guest_bp.get("/slots")
def list_slots():
    """Return generated free slots for one event type over the 14-day window."""
    event_type_id = request.args.get("eventTypeId")
    if event_type_id is None or not str(event_type_id).strip():
        raise validation_error("Query parameter eventTypeId is required.")

    storage: Storage = current_app.config["STORAGE"]
    slots = storage.list_available_slots(event_type_id.strip(), utc_now())
    if slots is None:
        raise not_found("Event type not found.")

    return jsonify(
        {
            "eventTypeId": event_type_id.strip(),
            "availableSlots": [serialize_slot(slot) for slot in slots],
        }
    )


@guest_bp.post("/bookings")
def create_booking():
    """Book a generated slot. guestName is collected at confirm time."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise validation_error("Request body must be a JSON object.")

    event_type_id = body.get("eventTypeId")
    if not isinstance(event_type_id, str) or not event_type_id.strip():
        raise validation_error("eventTypeId is required.")

    guest_name_raw = body.get("guestName")
    if not isinstance(guest_name_raw, str) or not guest_name_raw.strip():
        raise validation_error("guestName is required.")
    guest_name = guest_name_raw.strip()

    slot_start = parse_utc_timestamp(body.get("slotStart"))
    if slot_start is None:
        raise validation_error("slotStart must be a UTC ISO-8601 timestamp.")

    storage: Storage = current_app.config["STORAGE"]
    try:
        booking = storage.create_booking(
            event_type_id.strip(), slot_start, guest_name, utc_now()
        )
    except EventTypeNotFoundError as exc:
        raise not_found("Event type not found.") from exc
    except SlotConflictError as exc:
        raise _CONFLICT_ERRORS[exc.code]() from exc

    logger.bind(
        event="booking.created",
        event_type_id=booking.event_type_id,
        booking_id=booking.id,
        guest_name=booking.guest_name,
    ).info("booking.created")

    return jsonify(serialize_booking(booking)), 201
