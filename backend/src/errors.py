"""Structured API errors and Flask error handlers."""

from dataclasses import dataclass

from flask import Response, jsonify

from .logging_setup import log_event


@dataclass
class ApiError(Exception):
    """A documented API response failure."""

    code: str
    message: str
    status: int


def install_error_handlers(app) -> None:
    """Install uniform JSON responses for expected and unknown failures."""

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError) -> tuple[Response, int]:
        log_event("error", error_code=error.code, message=error.message)
        return jsonify(error={"code": error.code, "message": error.message}), error.status

    @app.errorhandler(404)
    def handle_not_found(_: Exception) -> tuple[Response, int]:
        error = ApiError("not_found", "Resource not found.", 404)
        return handle_api_error(error)
