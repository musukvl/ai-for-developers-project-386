"""HTTP API error types and constructors matching the TypeSpec error envelope."""

from __future__ import annotations


class ApiError(Exception):
    """Raised by request handlers to produce a JSON error body and HTTP status."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message

    def to_body(self) -> dict[str, dict[str, str]]:
        """Return the `{error: {code, message}}` envelope."""
        return {"error": {"code": self.code, "message": self.message}}


def validation_error(message: str) -> ApiError:
    """400: request body or query is missing, malformed, or fails validation."""
    return ApiError(400, "validation_error", message)


def not_found(message: str) -> ApiError:
    """404: the referenced event type or booking does not exist or is in the past."""
    return ApiError(404, "not_found", message)


def conflict(message: str) -> ApiError:
    """409: generic conflict, for example a duplicate event type id."""
    return ApiError(409, "conflict", message)


def slot_occupied_error() -> ApiError:
    """409: another booking already covers this clock interval."""
    return ApiError(409, "slot_occupied", "The selected slot is already booked.")


def slot_outside_window_error() -> ApiError:
    """409: the requested start is in the past or beyond the 14-day window."""
    return ApiError(409, "slot_outside_window", "The selected slot is outside the booking window.")


def slot_mismatch_error() -> ApiError:
    """409: slotStart is not on the event type's same-day duration grid."""
    return ApiError(409, "slot_mismatch", "The selected start time is not a valid slot.")


def future_bookings_exist_error() -> ApiError:
    """409: the event type still has upcoming bookings and cannot be deleted."""
    return ApiError(
        409,
        "future_bookings_exist",
        "Cannot delete this event type while upcoming bookings reference it.",
    )
