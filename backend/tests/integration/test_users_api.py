"""Integration tests for the Users API: POST /api/users."""


class TestEnterName:
    def test_registers_new_user_and_normalizes_name(self, client):
        c = client("empty.yml")
        response = c.post("/api/users", json={"name": "  Alex  "})
        assert response.status_code == 200
        assert response.get_json() == {"name": "alex", "isNew": True, "hasCalendar": False}

    def test_signs_in_existing_user_without_re_registering(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "Alex"})
        response = c.post("/api/users", json={"name": "ALEX"})
        assert response.get_json() == {"name": "alex", "isNew": False, "hasCalendar": False}

    def test_has_calendar_becomes_true_after_creation(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "alex"})
        c.post("/api/calendars", json={"ownerId": "alex"}, headers={"X-User-Name": "alex"})
        response = c.post("/api/users", json={"name": "alex"})
        assert response.get_json()["hasCalendar"] is True

    def test_invalid_normalized_name_is_rejected(self, client):
        c = client("empty.yml")
        response = c.post("/api/users", json={"name": "a"})
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_name_with_disallowed_characters_is_rejected_not_rewritten(self, client):
        c = client("empty.yml")
        response = c.post("/api/users", json={"name": "Sam Smith"})
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_missing_name_field_is_rejected(self, client):
        c = client("empty.yml")
        response = c.post("/api/users", json={})
        assert response.status_code == 400

    def test_no_user_name_header_required(self, client):
        c = client("empty.yml")
        response = c.post("/api/users", json={"name": "alex"})
        assert response.status_code == 200
