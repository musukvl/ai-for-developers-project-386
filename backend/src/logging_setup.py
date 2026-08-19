"""Structured logging: one flat JSON object per line, to stdout and to LOG_FILE.

Configured with a custom serializer plus `logger.patch`, not `serialize=True`,
because loguru's default serialization wraps every record in a nested
envelope. A flat object per line means a single `jq` selector reaches any
field and `grep` on a line yields a complete record.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from datetime import UTC

from loguru import logger as _base_logger

_file_write_lock = threading.Lock()


def _patch_record(record: dict) -> None:
    """Ensure every record has an `event`, defaulting freeform log calls to `log`."""
    record["extra"].setdefault("event", "log")


logger = _base_logger.patch(_patch_record)


def _record_to_json_line(record: dict) -> str:
    """Flatten a loguru record into the project's JSON Lines schema."""
    timestamp = record["time"].astimezone(UTC).isoformat(timespec="milliseconds")
    payload: dict[str, object] = {
        "ts": timestamp.replace("+00:00", "Z"),
        "level": record["level"].name,
    }
    extra = dict(record["extra"])
    payload["event"] = extra.pop("event", "log")
    payload.update(extra)
    return json.dumps(payload, default=str, ensure_ascii=False)


def _stdout_sink(message) -> None:
    sys.stdout.write(_record_to_json_line(message.record) + "\n")
    sys.stdout.flush()


def _make_file_sink(path: str):
    def sink(message) -> None:
        with _file_write_lock, open(path, "a", encoding="utf-8") as handle:
            handle.write(_record_to_json_line(message.record) + "\n")

    return sink


def configure_logging(log_level: str, log_file: str) -> None:
    """Reset loguru sinks and attach the flat JSON Lines sinks for stdout and `log_file`."""
    directory = os.path.dirname(log_file)
    if directory:
        os.makedirs(directory, exist_ok=True)

    _base_logger.remove()
    _base_logger.add(_stdout_sink, level=log_level)
    _base_logger.add(_make_file_sink(log_file), level=log_level)
