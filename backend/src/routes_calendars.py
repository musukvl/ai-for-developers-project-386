"""Shared calendar directory API available to signed-in users."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from src.auth import get_user_name
from src.serializers import serialize_calendar_directory
from src.storage import Storage

calendars_bp = Blueprint("calendars", __name__)


@calendars_bp.get("/api/calendars")
def list_calendars():
    """Return the public calendar directory in alphabetical owner-ID order."""
    storage: Storage = current_app.config["STORAGE"]
    get_user_name()
    return jsonify(serialize_calendar_directory(storage.list_calendar_owner_ids()))
