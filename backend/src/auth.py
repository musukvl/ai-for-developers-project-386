"""Extracts and validates the `X-User-Name` header shared by every non-public endpoint."""

from __future__ import annotations

from flask import request

from src.domain import is_valid_name, normalize_name
from src.errors import name_mismatch, validation_error


def get_user_name() -> str:
    """Return the normalized `X-User-Name` header, or raise `validation_error`."""
    raw_name = request.headers.get("X-User-Name")
    if not raw_name:
        raise validation_error("The X-User-Name header is required.")
    name = normalize_name(raw_name)
    if not is_valid_name(name):
        raise validation_error(
            "X-User-Name must be 3-64 characters using only lowercase letters, "
            "digits, and hyphens."
        )
    return name


def require_owner_match(user_name: str, owner_id: str) -> None:
    """Raise `name_mismatch` unless the caller's name equals the targeted owner."""
    if user_name != owner_id:
        raise name_mismatch()
