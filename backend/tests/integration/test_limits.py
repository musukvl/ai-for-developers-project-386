"""413 payload limit and Waitress SIGTERM shutdown."""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from tests.integration.helpers import iso, utc_today_at

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class TestPayloadLimit:
    def test_oversized_body_returns_413_and_next_request_succeeds(self, client):
        app_client = client("default_types.yml")
        oversized = "x" * (65 * 1024)
        too_large = app_client.post(
            "/api/bookings",
            data=oversized,
            content_type="application/json",
        )
        assert too_large.status_code == 413
        assert too_large.get_json()["error"]["code"] != "validation_error"

        ok = app_client.post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(utc_today_at(10, 0, day_offset=1)),
                "guestName": "Sam",
            },
        )
        assert ok.status_code == 201
        assert ok.get_json()["guestName"] == "Sam"


class TestSigterm:
    def test_waitress_exits_within_10_seconds(self, tmp_path: Path):
        port = _free_port()
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "index.html").write_text("<html>spa</html>", encoding="utf-8")

        env = os.environ.copy()
        env["SEED_FILE"] = str(_FIXTURES_DIR / "empty.yml")
        env["LOG_FILE"] = str(tmp_path / "sigterm.jsonl")
        env["PORT"] = str(port)
        env["STATIC_DIR"] = str(static_dir)
        env["PYTHONPATH"] = str(_BACKEND_ROOT)

        process = subprocess.Popen(
            [sys.executable, "-m", "src.app"],
            cwd=_BACKEND_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            _wait_for_health(port)
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=10)
            assert process.returncode in {0, -signal.SIGTERM}
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_health(port: int) -> None:
    url = f"http://127.0.0.1:{port}/api/health"
    deadline = time.monotonic() + 15
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
        time.sleep(0.1)
    raise AssertionError(f"Waitress did not become ready on port {port}: {last_error}")
