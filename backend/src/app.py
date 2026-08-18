"""Flask application factory."""

from pathlib import Path
from time import perf_counter
from uuid import uuid4

from flask import Flask, Response, g, request, send_from_directory
from loguru import logger

from .api import health, owner, users, visitor
from .config import Settings, load_settings
from .errors import ApiError, install_error_handlers
from .logging_setup import configure_logging, log_event
from .seed import load_seed
from .storage import CalendarStore


def create_app(settings: Settings | None = None) -> Flask:
    """Create a configured Calls Calendar Flask application."""
    runtime_settings = settings or load_settings()
    configure_logging(runtime_settings.log_level, runtime_settings.log_file)
    application = Flask(__name__, static_folder=None)
    application.extensions["settings"] = runtime_settings
    calendar_store = CalendarStore()
    application.extensions["calendar_store"] = calendar_store
    load_seed(calendar_store, runtime_settings.seed_file)
    _install_request_logging(application)
    install_error_handlers(application)
    application.register_blueprint(health.blueprint)
    application.register_blueprint(users.blueprint)
    application.register_blueprint(owner.blueprint)
    application.register_blueprint(visitor.blueprint)
    _install_spa_routes(application, runtime_settings.static_dir)
    return application


def _install_request_logging(application: Flask) -> None:
    @application.before_request
    def start_request() -> None:
        g.request_started = perf_counter()
        g.request_id = uuid4().hex[:6]
        g.log_context = logger.contextualize(request_id=g.request_id)
        g.log_context.__enter__()

    @application.after_request
    def end_request(response: Response) -> Response:
        started = getattr(g, "request_started", perf_counter())
        log_event(
            "request.end",
            method=request.method,
            path=request.path,
            user=request.headers.get("X-User-Name"),
            status=response.status_code,
            duration_ms=round((perf_counter() - started) * 1000, 2),
        )
        context = getattr(g, "log_context", None)
        if context is not None:
            context.__exit__(None, None, None)
        return response


def _install_spa_routes(application: Flask, static_dir: Path | None) -> None:
    if static_dir is None:

        @application.route("/", defaults={"path": ""})
        @application.route("/<path:path>")
        def no_static(path: str) -> tuple[object, int]:
            if path.startswith("api/"):
                raise ApiError("not_found", "Resource not found.", 404)
            raise ApiError("not_found", "Frontend build is not configured.", 404)

        return

    @application.route("/", defaults={"path": ""})
    @application.route("/<path:path>")
    def serve_spa(path: str):
        if path.startswith("api/"):
            raise ApiError("not_found", "Resource not found.", 404)
        candidate = static_dir / path
        if path and candidate.is_file():
            return send_from_directory(static_dir, path)
        return send_from_directory(static_dir, "index.html")
