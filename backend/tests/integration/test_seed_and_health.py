"""Integration tests for the health check, seed loading, and SPA/static fallback."""

from pathlib import Path

from src.app import create_app


class TestHealth:
    def test_reports_ok_and_configured_seed_file(self, client, make_app):
        app = make_app("empty.yml")
        c = app.test_client()
        response = c.get("/api/health")
        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "ok"
        assert body["seedFile"].endswith("empty.yml")

    def test_no_header_required(self, client):
        c = client("empty.yml")
        response = c.get("/api/health")
        assert response.status_code == 200


class TestUnknownApiPath:
    def test_unknown_api_path_returns_json_not_found(self, client):
        c = client("empty.yml")
        response = c.get("/api/does-not-exist")
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"


class TestSpaFallback:
    def test_unknown_path_without_static_dir_is_404(self, client):
        c = client("empty.yml")
        response = c.get("/cal/alex")
        assert response.status_code == 404

    def test_deep_link_falls_back_to_index_html_when_static_dir_configured(self, tmp_path):
        static_dir: Path = tmp_path / "dist"
        static_dir.mkdir()
        (static_dir / "index.html").write_text("<html>spa</html>", encoding="utf-8")

        fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"
        app = create_app(
            {
                "SEED_FILE": str(fixtures_dir / "empty.yml"),
                "LOG_FILE": str(tmp_path / "app.jsonl"),
                "STATIC_DIR": str(static_dir),
            }
        )
        c = app.test_client()

        response = c.get("/cal/alex")
        assert response.status_code == 200
        assert b"spa" in response.data

    def test_static_asset_is_served_directly(self, tmp_path):
        static_dir: Path = tmp_path / "dist"
        static_dir.mkdir()
        (static_dir / "index.html").write_text("<html>spa</html>", encoding="utf-8")
        (static_dir / "app.js").write_text("console.log('hi');", encoding="utf-8")

        fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"
        app = create_app(
            {
                "SEED_FILE": str(fixtures_dir / "empty.yml"),
                "LOG_FILE": str(tmp_path / "app.jsonl"),
                "STATIC_DIR": str(static_dir),
            }
        )
        c = app.test_client()

        response = c.get("/app.js")
        assert response.status_code == 200
        assert b"console.log" in response.data

    def test_unknown_api_path_returns_404_even_with_static_dir(self, tmp_path):
        static_dir: Path = tmp_path / "dist"
        static_dir.mkdir()
        (static_dir / "index.html").write_text("<html>spa</html>", encoding="utf-8")

        fixtures_dir = Path(__file__).resolve().parent.parent / "fixtures"
        app = create_app(
            {
                "SEED_FILE": str(fixtures_dir / "empty.yml"),
                "LOG_FILE": str(tmp_path / "app.jsonl"),
                "STATIC_DIR": str(static_dir),
            }
        )
        c = app.test_client()

        response = c.get("/api/does-not-exist")
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"
