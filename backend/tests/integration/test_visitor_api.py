"""Integration tests for the Visitor API."""

from .helpers import future_range, iso


def _register_and_create(c, name: str):
    c.post("/api/users", json={"name": name})
    c.post("/api/calendars", json={"ownerId": name}, headers={"X-User-Name": name})


class TestGetVisitorCalendar:
    def test_shows_available_slots_and_only_my_bookings(self, client):
        c = client("seeded_calendar.yml")
        response = c.get("/api/calendars/blake", headers={"X-User-Name": "casey"})
        assert response.status_code == 200
        body = response.get_json()
        assert body["ownerId"] == "blake"
        assert len(body["availableSlots"]) == 1
        assert len(body["myBookings"]) == 1
        assert body["myBookings"][0]["visitorName"] == "casey"

    def test_other_visitor_sees_no_bookings_of_their_own(self, client):
        c = client("seeded_calendar.yml")
        c.post("/api/users", json={"name": "dana"})
        response = c.get("/api/calendars/blake", headers={"X-User-Name": "dana"})
        assert response.get_json()["myBookings"] == []

    def test_owner_can_use_visitor_endpoint_on_own_calendar(self, client):
        c = client("seeded_calendar.yml")
        response = c.get("/api/calendars/blake", headers={"X-User-Name": "blake"})
        assert response.status_code == 200

    def test_not_found_for_missing_calendar(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "sam"})
        response = c.get("/api/calendars/alex", headers={"X-User-Name": "sam"})
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_not_found_for_malformed_owner_id(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "sam"})
        response = c.get("/api/calendars/Not Valid!", headers={"X-User-Name": "sam"})
        assert response.status_code == 404

    def test_header_required(self, client):
        c = client("seeded_calendar.yml")
        response = c.get("/api/calendars/blake")
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"


class TestCreateBooking:
    def test_books_a_published_slot(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        c.post("/api/users", json={"name": "sam"})
        start, end = future_range()
        c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end)},
            headers={"X-User-Name": "alex"},
        )
        response = c.post(
            "/api/calendars/alex/bookings",
            json={"slotStart": iso(start)},
            headers={"X-User-Name": "sam"},
        )
        assert response.status_code == 201
        body = response.get_json()
        assert body["visitorName"] == "sam"
        assert body["start"] == iso(start)
        assert "id" in body

    def test_double_booking_same_slot_is_conflict(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
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

    def test_booking_a_never_published_slot_is_conflict(self, client):
        c = client("empty.yml")
        _register_and_create(c, "alex")
        c.post("/api/users", json={"name": "sam"})
        start, _ = future_range()
        response = c.post(
            "/api/calendars/alex/bookings",
            json={"slotStart": iso(start)},
            headers={"X-User-Name": "sam"},
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "conflict"

    def test_missing_slot_start_is_validation_error(self, client):
        c = client("seeded_calendar.yml")
        response = c.post(
            "/api/calendars/blake/bookings", json={}, headers={"X-User-Name": "casey"}
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_unparseable_slot_start_is_validation_error(self, client):
        c = client("seeded_calendar.yml")
        response = c.post(
            "/api/calendars/blake/bookings",
            json={"slotStart": "not-a-timestamp"},
            headers={"X-User-Name": "casey"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_not_found_for_missing_calendar(self, client):
        c = client("empty.yml")
        c.post("/api/users", json={"name": "sam"})
        start, _ = future_range()
        response = c.post(
            "/api/calendars/alex/bookings",
            json={"slotStart": iso(start)},
            headers={"X-User-Name": "sam"},
        )
        assert response.status_code == 404


class TestCancelBookingAsVisitor:
    def test_cancels_own_booking_and_frees_slot(self, client):
        c = client("seeded_calendar.yml")
        response = c.delete(
            "/api/calendars/blake/bookings/seeded-booking-1", headers={"X-User-Name": "casey"}
        )
        assert response.status_code == 204

        after = c.get("/api/calendars/blake", headers={"X-User-Name": "casey"}).get_json()
        assert after["myBookings"] == []
        assert len(after["availableSlots"]) == 2

    def test_not_found_for_another_users_booking(self, client):
        c = client("seeded_calendar.yml")
        c.post("/api/users", json={"name": "dana"})
        response = c.delete(
            "/api/calendars/blake/bookings/seeded-booking-1", headers={"X-User-Name": "dana"}
        )
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_not_found_for_unknown_booking(self, client):
        c = client("seeded_calendar.yml")
        response = c.delete(
            "/api/calendars/blake/bookings/does-not-exist", headers={"X-User-Name": "casey"}
        )
        assert response.status_code == 404
