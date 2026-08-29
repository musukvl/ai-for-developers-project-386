"""Check-order tests: first failure decides the response."""

from tests.integration.helpers import iso, utc_today_at


class TestCheckOrder:
    def test_validation_wins_over_unknown_event_type(self, client):
        response = client("default_types.yml").post("/api/bookings", json={})
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_unknown_event_type_wins_over_slot_errors(self, client):
        response = client("default_types.yml").post(
            "/api/bookings",
            json={
                "eventTypeId": "does-not-exist",
                "slotStart": iso(utc_today_at(10, 17, day_offset=14)),
                "guestName": "Sam",
            },
        )
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_occupied_wins_over_outside_window_and_mismatch(self, client):
        c = client("seeded.yml")
        occupied_start = utc_today_at(10, 30, day_offset=1)
        response = c.post(
            "/api/bookings",
            json={
                "eventTypeId": "fifteen-minute-call",
                "slotStart": iso(occupied_start),
                "guestName": "Alex",
            },
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "slot_occupied"

    def test_outside_window_wins_over_mismatch(self, client):
        response = client("default_types.yml").post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(utc_today_at(10, 17, day_offset=14)),
                "guestName": "Sam",
            },
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "slot_outside_window"
