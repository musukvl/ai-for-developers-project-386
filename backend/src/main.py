"""Development and container entrypoint."""

from .app import create_app


def main() -> None:
    """Run the single-process threaded Flask server."""
    app = create_app()
    settings = app.extensions["settings"]
    app.run(host="0.0.0.0", port=settings.port, threaded=True)


if __name__ == "__main__":
    main()
