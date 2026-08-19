"""Users API: the only endpoint that does not require `X-User-Name`."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from src.domain import is_valid_name, normalize_name
from src.errors import validation_error
from src.logging_setup import logger
from src.storage import Storage

users_bp = Blueprint("users", __name__)


@users_bp.post("/api/users")
def enter_name():
    storage: Storage = current_app.config["STORAGE"]
    body = request.get_json(silent=True)
    raw_name = body.get("name") if isinstance(body, dict) else None
    if not isinstance(raw_name, str):
        raise validation_error("The 'name' field is required.")

    name = normalize_name(raw_name)
    if not is_valid_name(name):
        raise validation_error(
            "Name must be 3-64 characters using only letters, digits, spaces, and hyphens "
            "after normalization."
        )

    is_new = storage.register_user(name)
    has_calendar = storage.has_calendar(name)

    if is_new:
        logger.bind(event="user.registered", user=name).info("user.registered")

    return jsonify({"name": name, "isNew": is_new, "hasCalendar": has_calendar})
