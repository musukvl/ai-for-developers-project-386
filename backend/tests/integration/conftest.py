"""Shared fixtures for Flask integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.app import create_app

_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
_LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"


@pytest.fixture
def make_app(request: pytest.FixtureRequest):
    """Factory: build a Flask app for a named fixture file under tests/fixtures/."""

    def _make(fixture_name: str):
        _LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = _LOGS_DIR / f"{request.node.name}.jsonl"
        return create_app(
            {
                "SEED_FILE": str(_FIXTURES_DIR / fixture_name),
                "LOG_FILE": str(log_file),
                "STATIC_DIR": None,
            }
        )

    return _make


@pytest.fixture
def client(make_app):
    """Factory: build a Flask test client for a named fixture file."""

    def _client(fixture_name: str):
        return make_app(fixture_name).test_client()

    return _client
