"""Readiness probe used by the Docker image and by test harnesses."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def get_health():
    return jsonify({"status": "ok", "seedFile": current_app.config["SEED_FILE"]})
