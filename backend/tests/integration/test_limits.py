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

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class TestPayloadLimit:
    def test_oversized_body_returns_413(self, client):
        oversized = "x" * (65 * 1024)
        response = client("default_types.yml").post(
            "/api/bookings",
            data=oversized,
            content_type="application/json",
        )
        assert response.status_code == 413
        body = response.get_json()
        assert body["error"]["code"] != "validation_error"


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
