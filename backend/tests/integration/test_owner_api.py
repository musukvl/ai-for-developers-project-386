"""Integration tests for the Owner API."""

from datetime import timedelta

from .helpers import future_range, iso


def _register_and_create(c, name: str):
    c.post("/api/users", json={"name": name})
    return c.post("/api/calendars", json={"ownerId": name}, headers={"X-User-Name": name})


class TestCreateCalendar:
    def test_creates_calendar_for_current_user(self, client):
        c = client("empty.yml")
        response = _register_and_create(c, "alex")
        assert response.status_code == 201
        assert response.get_json() == {"ownerId": "alex", "calendarUrl": "/cal/alex"}

    def test_second_create_attempt_is_conflict(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        response = _register_and_create(c, "alex")
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "conflict"

    def test_owner_id_not_matching_header_is_name_mismatch(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "alex"})
        response = c.post(
            "/api/calendars", json={"ownerId": "sam"}, headers={"X-User-Name": "alex"}
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "name_mismatch"

    def test_missing_owner_id_is_validation_error(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "alex"})
        response = c.post("/api/calendars", json={}, headers={"X-User-Name": "alex"})
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_missing_header_is_validation_error(self, client):
        c = client("empty.yml")
        response = c.post("/api/calendars", json={"ownerId": "alex"})
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"


class TestGetOwnerCalendar:
    def test_owner_sees_slots_and_bookings(self, client):
        c = client("seeded_calendar.yml")
        response = c.get("/api/calendars/blake/owner", headers={"X-User-Name": "blake"})
        assert response.status_code == 200
        body = response.get_json()
        assert body["ownerId"] == "blake"
        assert len(body["availableSlots"]) == 1
        assert len(body["bookings"]) == 1
        assert body["bookings"][0]["visitorName"] == "casey"

    def test_mismatch_when_caller_is_not_owner(self, client):
        c = client("seeded_calendar.yml")
        response = c.get("/api/calendars/blake/owner", headers={"X-User-Name": "casey"})
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "name_mismatch"

    def test_mismatch_reported_even_when_calendar_does_not_exist(self, client):
        c = client("empty.yml")
        response = c.get("/api/calendars/ghost/owner", headers={"X-User-Name": "someone-else"})
        assert response.get_json()["error"]["code"] == "name_mismatch"

    def test_not_found_when_calendar_missing(self, client):
        c = client("empty.yml")
        response = c.get("/api/calendars/alex/owner", headers={"X-User-Name": "alex"})
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"


class TestAddAvailability:
    def test_publishes_two_slots_for_a_one_hour_range(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        start, end = future_range()
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end)},
            headers={"X-User-Name": "alex"},
        )
        assert response.status_code == 200
        slots = response.get_json()["availableSlots"]
        assert [s["start"] for s in slots] == [iso(start), iso(start + timedelta(minutes=30))]

    def test_overlapping_range_does_not_duplicate_slots(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        start, end = future_range(duration=timedelta(hours=1))
        c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end)},
            headers={"X-User-Name": "alex"},
        )
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end + timedelta(minutes=30))},
            headers={"X-User-Name": "alex"},
        )
        assert response.status_code == 200
        assert len(response.get_json()["availableSlots"]) == 3

    def test_off_boundary_start_is_validation_error(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        start, end = future_range()
        off_boundary_start = iso(start + timedelta(minutes=15))
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": off_boundary_start, "end": iso(end)},
            headers={"X-User-Name": "alex"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_end_not_after_start_is_validation_error(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        start, _ = future_range()
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(start)},
            headers={"X-User-Name": "alex"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_outside_horizon_is_validation_error(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        start, end = future_range(start_offset=timedelta(days=30))
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end)},
            headers={"X-User-Name": "alex"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_mismatch_when_caller_is_not_owner(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        c.post("/api/users", json={"name": "sam"})
        start, end = future_range()
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end)},
            headers={"X-User-Name": "sam"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "name_mismatch"

    def test_not_found_when_calendar_missing(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "alex"})
        start, end = future_range()
        response = c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end)},
            headers={"X-User-Name": "alex"},
        )
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"


class TestRemoveAvailabilitySlot:
    def test_removes_the_only_free_slot_from_seed(self, client):
        c = client("seeded_calendar.yml")
        calendar = c.get(
            "/api/calendars/blake/owner", headers={"X-User-Name": "blake"}
        ).get_json()
        free_slot_start = calendar["availableSlots"][0]["start"]
        encoded = free_slot_start.replace(":", "%3A")
        response = c.delete(
            f"/api/calendars/blake/availability/{encoded}", headers={"X-User-Name": "blake"}
        )
        assert response.status_code == 204

        after = c.get("/api/calendars/blake/owner", headers={"X-User-Name": "blake"}).get_json()
        assert after["availableSlots"] == []

    def test_removing_a_booked_slot_is_conflict(self, client):
        c = client("seeded_calendar.yml")
        calendar = c.get(
            "/api/calendars/blake/owner", headers={"X-User-Name": "blake"}
        ).get_json()
        booked_start = calendar["bookings"][0]["start"]
        encoded = booked_start.replace(":", "%3A")
        response = c.delete(
            f"/api/calendars/blake/availability/{encoded}", headers={"X-User-Name": "blake"}
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "conflict"

    def test_removing_neighbouring_slot_does_not_affect_booking(self, client):
        c = client("seeded_calendar.yml")
        calendar = c.get(
            "/api/calendars/blake/owner", headers={"X-User-Name": "blake"}
        ).get_json()
        free_slot_start = calendar["availableSlots"][0]["start"]
        encoded = free_slot_start.replace(":", "%3A")
        c.delete(f"/api/calendars/blake/availability/{encoded}", headers={"X-User-Name": "blake"})

        after = c.get("/api/calendars/blake/owner", headers={"X-User-Name": "blake"}).get_json()
        assert len(after["bookings"]) == 1

    def test_not_found_for_unparseable_slot_start(self, client):
        c = client("seeded_calendar.yml")
        response = c.delete(
            "/api/calendars/blake/availability/not-a-timestamp",
            headers={"X-User-Name": "blake"},
        )
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_mismatch_when_caller_is_not_owner(self, client):
        c = client("seeded_calendar.yml")
        response = c.delete(
            "/api/calendars/blake/availability/2026-08-01T10%3A00%3A00Z",
            headers={"X-User-Name": "casey"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "name_mismatch"


class TestCancelBookingAsOwner:
    def test_cancels_and_frees_the_slot(self, client):
        c = client("seeded_calendar.yml")
        response = c.delete(
            "/api/calendars/blake/owner/bookings/seeded-booking-1",
            headers={"X-User-Name": "blake"},
        )
        assert response.status_code == 204

        after = c.get("/api/calendars/blake/owner", headers={"X-User-Name": "blake"}).get_json()
        assert after["bookings"] == []
        assert len(after["availableSlots"]) == 2

    def test_not_found_for_unknown_booking(self, client):
        c = client("seeded_calendar.yml")
        response = c.delete(
            "/api/calendars/blake/owner/bookings/does-not-exist",
            headers={"X-User-Name": "blake"},
        )
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_mismatch_when_caller_is_not_owner(self, client):
        c = client("seeded_calendar.yml")
        response = c.delete(
            "/api/calendars/blake/owner/bookings/seeded-booking-1",
            headers={"X-User-Name": "casey"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "name_mismatch"
