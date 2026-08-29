"""Structured JSON Lines logging to stdout and an optional log file."""

from __future__ import annotations

import json
import sys
from datetime import UTC
from pathlib import Path

from loguru import logger

_CONFIGURED = False


def configure_logging(level: str, log_file: str | None) -> None:
    """Replace the default loguru sink with JSON Lines sinks.

    One sink writes to stdout. When `log_file` is set, a second sink appends
    the same records to that path. Subsequent calls only adjust levels so
    tests can rebuild the app without stacking handlers.
    """
    global _CONFIGURED

    if _CONFIGURED:
        logger.remove()

    logger.remove()
    logger.add(_json_sink, level=level, format="{message}")

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(_file_sink(path), level=level, format="{message}")

    _CONFIGURED = True


def _serialize(record: dict) -> str:
    extra = record["extra"]
    payload: dict[str, object] = {
        "ts": record["time"].astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "level": record["level"].name,
        "event": extra.get("event", record["message"]),
    }
    if "request_id" in extra:
        payload["request_id"] = extra["request_id"]
    for key, value in extra.items():
        if key in {"event", "request_id"}:
            continue
        payload[key] = value
    return json.dumps(payload, default=str)


def _json_sink(message: object) -> None:
    sys.stdout.write(_serialize(message.record) + "\n")


def _file_sink(path: Path):
    def _write(message: object) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(_serialize(message.record) + "\n")

    return _write
