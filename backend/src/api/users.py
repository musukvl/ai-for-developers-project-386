"""User entry endpoint."""

from flask import Blueprint, jsonify

from ..errors import ApiError
from ..logging_setup import log_event
from ..names import validate_name
from .common import json_object, store

blueprint = Blueprint("users", __name__, url_prefix="/api")


@blueprint.post("/users")
def enter_name() -> tuple[object, int]:
    """Register or re-enter an identity used by the SPA."""
    body = json_object()
    try:
        name = validate_name(body.get("name"))
    except ValueError as error:
        raise ApiError("validation_error", str(error), 400) from error
    is_new = store().register_user(name)
    log_event("user.registered", user=name, is_new=is_new)
    return jsonify(name=name, isNew=is_new, hasCalendar=store().has_calendar(name)), 200
