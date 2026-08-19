"""Converts domain objects into the JSON shapes documented in spec/api.md."""

from __future__ import annotations

from src.domain import Booking, Slot, format_utc_timestamp


def serialize_slot(slot: Slot) -> dict:
    return {"start": format_utc_timestamp(slot.start), "end": format_utc_timestamp(slot.end)}


def serialize_booking(booking: Booking) -> dict:
    return {
        "id": booking.id,
        "start": format_utc_timestamp(booking.start),
        "end": format_utc_timestamp(booking.end),
        "visitorName": booking.visitor_name,
    }


def serialize_visitor_calendar(
    owner_id: str, available_slots: list[Slot], my_bookings: list[Booking]
) -> dict:
    return {
        "ownerId": owner_id,
        "availableSlots": [serialize_slot(slot) for slot in available_slots],
        "myBookings": [serialize_booking(booking) for booking in my_bookings],
    }


def serialize_owner_calendar(
    owner_id: str, available_slots: list[Slot], bookings: list[Booking]
) -> dict:
    return {
        "ownerId": owner_id,
        "availableSlots": [serialize_slot(slot) for slot in available_slots],
        "bookings": [serialize_booking(booking) for booking in bookings],
    }
