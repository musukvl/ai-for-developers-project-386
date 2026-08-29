"""Readiness probe for the API and the Docker image."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def get_health():
    """Return ok plus the configured seed file path."""
    return jsonify({"status": "ok", "seedFile": current_app.config["SEED_FILE"]})
