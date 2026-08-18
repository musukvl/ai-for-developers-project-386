"""Flat JSON Lines logging configuration."""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger

EVENTS = frozenset(
    {
        "request.end",
        "user.registered",
        "calendar.created",
        "availability.added",
        "slot.removed",
        "booking.created",
        "booking.cancelled",
        "seed.loaded",
        "error",
    }
)


def configure_logging(level: str, log_file: Path) -> None:
    """Configure loguru to write flat JSON records to stdout and a file."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    patched = logger.patch(_patch_record)
    patched.add(sys.stdout, level=level, format=_escaped_serialized_record)
    patched.add(str(log_file), level=level, format=_escaped_serialized_record)


def log_event(event: str, **fields: Any) -> None:
    """Emit a documented domain event."""
    if event not in EVENTS:
        raise ValueError(f"Unsupported log event: {event}")
    logger.bind(event=event, **fields).info(event)


def _patch_record(record: dict[str, Any]) -> None:
    extra = record["extra"]
    extra.setdefault("event", "error" if record["level"].name == "ERROR" else "request.end")
    extra.setdefault("request_id", None)


def _serialize_record(record: dict[str, Any]) -> str:
    payload = {
        "ts": datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "level": record["level"].name,
        **record["extra"],
    }
    return json.dumps(payload, default=str, separators=(",", ":")) + "\n"


def _escaped_serialized_record(record: dict[str, Any]) -> str:
    """Escape braces because loguru applies ``str.format`` after callable formats."""
    return _serialize_record(record).replace("{", "{{").replace("}", "}}")
