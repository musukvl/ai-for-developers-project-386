"""Integration tests for owner event-type and booking administration."""

from tests.integration.helpers import iso, utc_today_at


class TestCreateEventType:
    def test_creates_an_event_type(self, client):
        c = client("empty.yml")
        response = c.post(
            "/api/owner/event-types",
            json={
                "id": "strategy-session",
                "title": "Strategy session",
                "description": "Discuss the project roadmap.",
                "durationMinutes": 30,
            },
        )
        assert response.status_code == 200
        assert response.get_json()["id"] == "strategy-session"
        catalog = c.get("/api/event-types").get_json()["eventTypes"]
        assert catalog[0]["title"] == "Strategy session"

    def test_duplicate_id_is_conflict(self, client):
        c = client("default_types.yml")
        response = c.post(
            "/api/owner/event-types",
            json={
                "id": "thirty-minute-call",
                "title": "Other",
                "description": "Duplicate.",
                "durationMinutes": 15,
            },
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "conflict"

    def test_duration_less_than_one_is_validation_error(self, client):
        response = client("empty.yml").post(
            "/api/owner/event-types",
            json={
                "id": "bad",
                "title": "Bad",
                "description": "Too short.",
                "durationMinutes": 0,
            },
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"


class TestDeleteEventType:
    def test_deletes_when_no_upcoming_bookings(self, client):
        c = client("default_types.yml")
        response = c.delete("/api/owner/event-types/fifteen-minute-call")
        assert response.status_code == 204
        ids = [item["id"] for item in c.get("/api/event-types").get_json()["eventTypes"]]
        assert "fifteen-minute-call" not in ids

    def test_future_bookings_block_delete(self, client):
        c = client("seeded.yml")
        response = c.delete("/api/owner/event-types/thirty-minute-call")
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "future_bookings_exist"

    def test_unknown_event_type_is_not_found(self, client):
        response = client("empty.yml").delete("/api/owner/event-types/missing")
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_past_bookings_do_not_block_delete(self, client):
        c = client("past_data.yml")
        c.delete("/api/owner/bookings/upcoming-booking-1")
        response = c.delete("/api/owner/event-types/thirty-minute-call")
        assert response.status_code == 204


class TestOwnerBookings:
    def test_lists_upcoming_only_with_guest_name(self, client):
        response = client("past_data.yml").get("/api/owner/bookings")
        assert response.status_code == 200
        bookings = response.get_json()["bookings"]
        assert [item["id"] for item in bookings] == ["upcoming-booking-1"]
        assert bookings[0]["guestName"] == "Sam"
        assert bookings[0]["eventTypeTitle"] == "30m call"

    def test_cancel_restores_generated_slot(self, client):
        c = client("seeded.yml")
        slot_start = iso(utc_today_at(10, 30, day_offset=1))
        before = c.get("/api/slots?eventTypeId=thirty-minute-call").get_json()["availableSlots"]
        assert slot_start not in [slot["start"] for slot in before]

        cancel = c.delete("/api/owner/bookings/seed-booking-1")
        assert cancel.status_code == 204

        after = c.get("/api/slots?eventTypeId=thirty-minute-call").get_json()["availableSlots"]
        assert slot_start in [slot["start"] for slot in after]
        assert c.get("/api/owner/bookings").get_json()["bookings"] == []

    def test_cancel_unknown_or_past_is_not_found(self, client):
        c = client("past_data.yml")
        missing = c.delete("/api/owner/bookings/does-not-exist")
        assert missing.status_code == 404
        past = c.delete("/api/owner/bookings/past-booking-1")
        assert past.status_code == 404
        assert past.get_json()["error"]["code"] == "not_found"
