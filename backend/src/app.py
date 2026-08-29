"""Flask application factory and process entrypoint."""

from __future__ import annotations

import os
import signal
import time
import uuid
from pathlib import Path

from flask import Flask, Response, g, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from src.errors import ApiError, not_found
from src.logging_setup import configure_logging, logger
from src.routes_guest import guest_bp
from src.routes_health import health_bp
from src.routes_owner import owner_bp
from src.seed import SeedError, load_seed
from src.storage import Storage

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_MAX_CONTENT_LENGTH = 64 * 1024


def create_app(config: dict | None = None) -> Flask:
    """Build a fully configured Flask app: logging, seeded storage, routes, errors.

    `config` lets tests override settings (chiefly `SEED_FILE` and `LOG_FILE`)
    without mutating process environment variables.
    """
    settings = _resolve_settings(config)
    configure_logging(settings["LOG_LEVEL"], settings["LOG_FILE"])

    app = Flask(__name__, static_folder=None)
    app.config.update(settings)
    app.config["MAX_CONTENT_LENGTH"] = _MAX_CONTENT_LENGTH

    storage = Storage()
    app.config["STORAGE"] = storage

    try:
        load_seed(storage, _resolve_seed_path(settings["SEED_FILE"]))
    except SeedError as exc:
        logger.bind(event="error", error_code="seed_error", message=str(exc)).error(str(exc))
        raise

    app.register_blueprint(health_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(owner_bp)

    _register_request_logging(app)
    _register_error_handlers(app)
    _register_spa_fallback(app, settings["STATIC_DIR"])

    return app


def serve_app() -> None:
    """Run the app: Flask's threaded server in development, Waitress in Docker."""
    application = create_app()
    port = application.config["PORT"]
    if application.config.get("STATIC_DIR"):
        from waitress.server import create_server

        logger.bind(event="server.start", server="waitress", port=port).info("server.start")
        server = create_server(application, host="0.0.0.0", port=port, threads=8)

        def _handle_term(_signum: int, _frame: object) -> None:
            server.close()
            raise SystemExit(0)

        signal.signal(signal.SIGTERM, _handle_term)
        server.run()
        return

    logger.bind(event="server.start", server="flask", port=port).info("server.start")
    application.run(host="0.0.0.0", port=port, threaded=True)


def _resolve_settings(overrides: dict | None) -> dict:
    settings = {
        "SEED_FILE": os.environ.get("SEED_FILE", "src/seed.yml"),
        "PORT": int(os.environ.get("PORT", "5000")),
        "LOG_LEVEL": os.environ.get("LOG_LEVEL", "INFO"),
        "LOG_FILE": os.environ.get("LOG_FILE", "logs/app.jsonl"),
        "STATIC_DIR": os.environ.get("STATIC_DIR"),
    }
    if overrides:
        settings.update(overrides)
    return settings


def _resolve_seed_path(seed_file: str) -> str:
    """Resolve a possibly-relative `SEED_FILE` against the `backend/` directory."""
    path = Path(seed_file)
    return str(path) if path.is_absolute() else str(_BACKEND_ROOT / path)


def _register_request_logging(app: Flask) -> None:
    @app.before_request
    def _start_request() -> None:
        g.request_id = uuid.uuid4().hex[:12]
        g.request_start = time.monotonic()
        g.logger_context = logger.contextualize(request_id=g.request_id)
        g.logger_context.__enter__()

    @app.after_request
    def _end_request(response: Response) -> Response:
        duration_ms = (time.monotonic() - g.get("request_start", time.monotonic())) * 1000
        logger.bind(
            event="request.end",
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
        ).info("request.end")
        return response

    @app.teardown_request
    def _teardown_request(_exc: BaseException | None) -> None:
        context = g.pop("logger_context", None)
        if context is not None:
            context.__exit__(None, None, None)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def _handle_api_error(error: ApiError):
        logger.bind(event="error", error_code=error.code, message=error.message).warning(
            error.message
        )
        return jsonify(error.to_body()), error.status

    @app.errorhandler(RequestEntityTooLarge)
    def _handle_too_large(_error: RequestEntityTooLarge):
        message = "Request body is too large."
        logger.bind(event="error", error_code="payload_too_large", message=message).warning(
            message
        )
        return jsonify({"error": {"code": "payload_too_large", "message": message}}), 413

    @app.errorhandler(HTTPException)
    def _handle_http_exception(error: HTTPException):
        message = error.description or str(error)
        logger.bind(event="error", error_code="http_error", message=message).warning(message)
        return jsonify({"error": {"code": "http_error", "message": message}}), error.code or 500

    @app.errorhandler(Exception)
    def _handle_unexpected_error(error: Exception):
        logger.bind(event="error", error_code="internal_error", message=str(error)).exception(
            "Unhandled exception"
        )
        body = {"error": {"code": "internal_error", "message": "Internal server error."}}
        return jsonify(body), 500


def _register_spa_fallback(app: Flask, static_dir: str | None) -> None:
    """Serve the built SPA in production; return JSON 404 for unknown `/api/*` paths."""

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def _serve_spa(path: str):
        if path.startswith("api/"):
            return jsonify(not_found("The requested API endpoint does not exist.").to_body()), 404

        if not static_dir:
            return jsonify(not_found("Not found.").to_body()), 404

        candidate = Path(static_dir) / path
        if path and candidate.is_file():
            return send_from_directory(static_dir, path)
        return send_from_directory(static_dir, "index.html")


if __name__ == "__main__":
    serve_app()
