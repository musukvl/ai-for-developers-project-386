"""Visitor API: read any public calendar, book a slot, and cancel your own booking.

Owner and visitor logic never mix in one handler; the only thing shared with
the owner module is storage and the neutral `calendar_lookup` helper.
"""

from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, current_app, jsonify, request

from src.auth import get_user_name
from src.calendar_lookup import ensure_calendar_exists
from src.domain import generate_booking_id, parse_utc_timestamp
from src.errors import conflict, not_found, validation_error
from src.logging_setup import logger
from src.serializers import serialize_booking, serialize_visitor_calendar
from src.storage import BookingNotFoundError, SlotUnavailableError, Storage

visitor_bp = Blueprint("visitor", __name__)


@visitor_bp.get("/api/calendars/<owner_id>")
def get_visitor_calendar(owner_id: str):
    storage: Storage = current_app.config["STORAGE"]
    user_name = get_user_name()
    ensure_calendar_exists(storage, owner_id)

    now = datetime.now(UTC)
    available_slots = storage.get_available_slots(owner_id, now)
    my_bookings = storage.get_my_bookings(owner_id, user_name, now)
    return jsonify(serialize_visitor_calendar(owner_id, available_slots, my_bookings))


@visitor_bp.post("/api/calendars/<owner_id>/bookings")
def create_booking(owner_id: str):
    storage: Storage = current_app.config["STORAGE"]
    user_name = get_user_name()
    ensure_calendar_exists(storage, owner_id)

    now = datetime.now(UTC)
    body = request.get_json(silent=True)
    slot_start_raw = body.get("slotStart") if isinstance(body, dict) else None
    slot_start = parse_utc_timestamp(slot_start_raw)
    if slot_start is None:
        raise validation_error("The 'slotStart' field must be a UTC ISO 8601 timestamp.")

    booking_id = generate_booking_id()
    try:
        booking = storage.create_booking(owner_id, slot_start, user_name, booking_id, now)
    except SlotUnavailableError as exc:
        raise conflict("No free slot starts at that instant.") from exc

    logger.bind(
        event="booking.created",
        owner_id=owner_id,
        visitor_name=user_name,
        slot_start=slot_start.isoformat(),
        booking_id=booking.id,
    ).info("booking.created")

    return jsonify(serialize_booking(booking)), 201


@visitor_bp.delete("/api/calendars/<owner_id>/bookings/<booking_id>")
def cancel_booking_as_visitor(owner_id: str, booking_id: str):
    storage: Storage = current_app.config["STORAGE"]
    user_name = get_user_name()
    ensure_calendar_exists(storage, owner_id)

    now = datetime.now(UTC)
    try:
        storage.cancel_booking_as_visitor(owner_id, booking_id, user_name, now)
    except BookingNotFoundError as exc:
        raise not_found("Booking not found.") from exc

    logger.bind(
        event="booking.cancelled", owner_id=owner_id, booking_id=booking_id, cancelled_by="visitor"
    ).info("booking.cancelled")

    return "", 204
