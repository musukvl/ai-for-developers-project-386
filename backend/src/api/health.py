"""Health-check endpoint."""

from flask import Blueprint, current_app, jsonify

blueprint = Blueprint("health", __name__, url_prefix="/api")


@blueprint.get("/health")
def health() -> tuple[object, int]:
    """Report process readiness and the active seed fixture."""
    settings = current_app.extensions["settings"]
    return jsonify(status="ok", seedFile=str(settings.seed_file)), 200
