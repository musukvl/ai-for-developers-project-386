"""Integration tests for the fixed check order documented in spec/api.md.

Checks run in a fixed order and the first failure decides the response:
header validity, then name_mismatch, then existence-and-not-past, then body
validation, then conflict.
"""

from .helpers import day_offset_instant, future_range, iso


class TestHeaderCheckedFirst:
    def test_missing_header_wins_over_missing_calendar(self, client):
        c = client("empty.yml")
        response = c.get("/api/calendars/ghost/owner")
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_invalid_header_wins_over_name_mismatch(self, client):
        c = client("empty.yml")
        response = c.get(
            "/api/calendars/alex/owner", headers={"X-User-Name": "Not Valid!"}
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"


class TestMismatchCheckedBeforeExistence:
    def test_mismatch_on_nonexistent_calendar_is_still_mismatch(self, client):
        c = client("empty.yml")
        response = c.get(
            "/api/calendars/alex/owner", headers={"X-User-Name": "someone-else"}
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "name_mismatch"

    def test_mismatch_needs_no_lookup_even_for_malformed_path_owner(self, client):
        c = client("empty.yml")
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": "2026-08-01T10:00:00Z", "end": "2026-08-01T11:00:00Z"},
            headers={"X-User-Name": "sam"},
        )
        assert response.get_json()["error"]["code"] == "name_mismatch"


class TestPathSlotStartVsBodySlotStart:
    def test_unparseable_path_slot_start_is_not_found(self, client):
        c = client("seeded_calendar.yml")
        response = c.delete(
            "/api/calendars/blake/availability/garbage", headers={"X-User-Name": "blake"}
        )
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_unparseable_body_slot_start_is_validation_error(self, client):
        c = client("seeded_calendar.yml")
        response = c.post(
            "/api/calendars/blake/bookings",
            json={"slotStart": "garbage"},
            headers={"X-User-Name": "casey"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"


class TestPastEntriesAreInvisible:
    def test_past_available_slot_cannot_be_removed(self, client):
        c = client("past_data.yml")
        past_slot = day_offset_instant(-2, 10, 30)
        encoded = iso(past_slot).replace(":", "%3A")
        response = c.delete(
            f"/api/calendars/dana/availability/{encoded}", headers={"X-User-Name": "dana"}
        )
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_past_slot_cannot_be_booked(self, client):
        c = client("past_data.yml")
        c.post("/api/users", json={"name": "sam"})
        past_slot = day_offset_instant(-2, 10, 30)
        response = c.post(
            "/api/calendars/dana/bookings",
            json={"slotStart": iso(past_slot)},
            headers={"X-User-Name": "sam"},
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "conflict"

    def test_past_booking_cannot_be_cancelled_by_owner(self, client):
        c = client("past_data.yml")
        response = c.delete(
            "/api/calendars/dana/owner/bookings/past-booking-1", headers={"X-User-Name": "dana"}
        )
        assert response.status_code == 404

    def test_past_booking_cannot_be_cancelled_by_visitor(self, client):
        c = client("past_data.yml")
        response = c.delete(
            "/api/calendars/dana/bookings/past-booking-1", headers={"X-User-Name": "erin"}
        )
        assert response.status_code == 404

    def test_past_entries_are_absent_from_get_responses(self, client):
        c = client("past_data.yml")
        response = c.get("/api/calendars/dana/owner", headers={"X-User-Name": "dana"}).get_json()
        assert response["availableSlots"] == [
            {
                "start": iso(day_offset_instant(1, 10, 0)),
                "end": iso(day_offset_instant(1, 10, 30)),
            }
        ]
        assert response["bookings"] == []


class TestBodyValidationAfterExistenceCheck:
    def test_malformed_body_on_missing_calendar_is_not_found(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "alex"})
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": "not-a-timestamp"},
            headers={"X-User-Name": "alex"},
        )
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"


class TestConflictCheckedLast:
    def test_valid_second_booking_of_same_slot_is_conflict_not_earlier_error(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "alex"})
        c.post("/api/calendars", json={"ownerId": "alex"}, headers={"X-User-Name": "alex"})
        c.post("/api/users", json={"name": "sam"})
        c.post("/api/users", json={"name": "dana"})
        start, end = future_range()
        c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end)},
            headers={"X-User-Name": "alex"},
        )
        c.post(
            "/api/calendars/alex/bookings",
            json={"slotStart": iso(start)},
            headers={"X-User-Name": "sam"},
        )
        response = c.post(
            "/api/calendars/alex/bookings",
            json={"slotStart": iso(start)},
            headers={"X-User-Name": "dana"},
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "conflict"
