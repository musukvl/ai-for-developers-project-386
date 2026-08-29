"""Integration tests for health, unknown API paths, and SPA fallback."""

from pathlib import Path

import pytest

from src.app import create_app
from src.seed import SeedError


class TestHealth:
    def test_health_returns_ok_and_seed_file(self, client):
        response = client("default_types.yml").get("/api/health")
        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "ok"
        assert body["seedFile"].endswith("default_types.yml")

    def test_unknown_api_path_returns_json_not_found(self, client):
        response = client("empty.yml").get("/api/does-not-exist")
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_invalid_seed_aborts_startup(self, tmp_path: Path, request):
        seed = tmp_path / "bad.yml"
        seed.write_text("owner: demo-owner\neventTypes: not-a-list\n", encoding="utf-8")
        log_file = tmp_path / f"{request.node.name}.jsonl"
        with pytest.raises(SeedError):
            create_app({"SEED_FILE": str(seed), "LOG_FILE": str(log_file), "STATIC_DIR": None})

    def test_deep_link_falls_back_to_index_html(self, tmp_path: Path, request):
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "index.html").write_text("<html>spa</html>", encoding="utf-8")
        fixtures = Path(__file__).resolve().parent.parent / "fixtures"
        app = create_app(
            {
                "SEED_FILE": str(fixtures / "empty.yml"),
                "LOG_FILE": str(tmp_path / f"{request.node.name}.jsonl"),
                "STATIC_DIR": str(static_dir),
            }
        )
        response = app.test_client().get("/owner")
        assert response.status_code == 200
        assert b"spa" in response.data
