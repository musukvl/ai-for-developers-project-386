"""Integration tests for the public calendar directory API."""


class TestCalendarDirectory:
    def test_returns_empty_directory_when_no_calendars_exist(self, client):
        response = client("empty.yml").get("/api/calendars", headers={"X-User-Name": "sam"})

        assert response.status_code == 200
        assert response.get_json() == {"calendars": []}

    def test_requires_a_valid_user_name_header(self, client):
        c = client("empty.yml")

        missing_header = c.get("/api/calendars")
        invalid_header = c.get("/api/calendars", headers={"X-User-Name": "Not Valid!"})

        assert missing_header.status_code == 400
        assert missing_header.get_json()["error"]["code"] == "validation_error"
        assert invalid_header.status_code == 400
        assert invalid_header.get_json()["error"]["code"] == "validation_error"

    def test_returns_owner_ids_in_alphabetical_order(self, client):
        response = client("calendar_directory.yml").get(
            "/api/calendars", headers={"X-User-Name": "visitor"}
        )

        assert response.status_code == 200
        assert response.get_json() == {
            "calendars": [{"ownerId": "alex"}, {"ownerId": "blake"}, {"ownerId": "zoe"}]
        }

    def test_includes_a_newly_created_calendar(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "alex"})
        c.post("/api/calendars", json={"ownerId": "alex"}, headers={"X-User-Name": "alex"})

        response = c.get("/api/calendars", headers={"X-User-Name": "alex"})

        assert response.status_code == 200
        assert response.get_json() == {"calendars": [{"ownerId": "alex"}]}
