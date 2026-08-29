"""JSON serializers for API response bodies."""

from __future__ import annotations

from src.domain import Booking, EventType, Slot, format_utc_timestamp


def serialize_event_type(event_type: EventType) -> dict[str, str | int]:
    """Serialize an event type for the catalog and owner create responses."""
    return {
        "id": event_type.id,
        "title": event_type.title,
        "description": event_type.description,
        "durationMinutes": event_type.duration_minutes,
    }


def serialize_slot(slot: Slot) -> dict[str, str]:
    """Serialize a generated slot as UTC ISO-8601 timestamps."""
    return {"start": format_utc_timestamp(slot.start), "end": format_utc_timestamp(slot.end)}


def serialize_booking(booking: Booking) -> dict[str, str]:
    """Serialize a booking including the guest name collected at confirm time."""
    return {
        "id": booking.id,
        "eventTypeId": booking.event_type_id,
        "eventTypeTitle": booking.event_type_title,
        "start": format_utc_timestamp(booking.start),
        "end": format_utc_timestamp(booking.end),
        "guestName": booking.guest_name,
    }
