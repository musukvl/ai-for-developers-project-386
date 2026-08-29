"""Integration tests for the guest catalog, slots, and booking API."""

from datetime import timedelta

from tests.integration.helpers import iso, utc_today_at


class TestListEventTypes:
    def test_lists_seeded_types(self, client):
        response = client("default_types.yml").get("/api/event-types")
        assert response.status_code == 200
        ids = [item["id"] for item in response.get_json()["eventTypes"]]
        assert ids == ["fifteen-minute-call", "thirty-minute-call"]

    def test_empty_catalog(self, client):
        response = client("empty.yml").get("/api/event-types")
        assert response.get_json() == {"eventTypes": []}


class TestListSlots:
    def test_missing_event_type_id_is_validation_error(self, client):
        response = client("default_types.yml").get("/api/slots")
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"

    def test_unknown_event_type_is_not_found(self, client):
        response = client("default_types.yml").get("/api/slots?eventTypeId=missing")
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "not_found"

    def test_slots_are_sorted_and_exclude_occupied(self, client):
        c = client("seeded.yml")
        response = c.get("/api/slots?eventTypeId=thirty-minute-call")
        assert response.status_code == 200
        starts = [slot["start"] for slot in response.get_json()["availableSlots"]]
        assert starts == sorted(starts)
        assert iso(utc_today_at(10, 30, day_offset=1)) not in starts


class TestCreateBooking:
    def test_books_a_generated_slot_by_event_type(self, client):
        c = client("default_types.yml")
        slot_start = utc_today_at(10, 0, day_offset=1)
        response = c.post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(slot_start),
                "guestName": "  Sam  ",
            },
        )
        assert response.status_code == 201
        body = response.get_json()
        assert body["guestName"] == "Sam"
        assert body["eventTypeId"] == "thirty-minute-call"
        assert body["eventTypeTitle"] == "30m call"
        assert body["start"] == iso(slot_start)
        assert body["end"] == iso(slot_start + timedelta(minutes=30))
        assert body["id"]

        slots = c.get("/api/slots?eventTypeId=thirty-minute-call").get_json()["availableSlots"]
        assert iso(slot_start) not in [slot["start"] for slot in slots]

    def test_cross_type_conflict_returns_slot_occupied(self, client):
        c = client("default_types.yml")
        slot_start = utc_today_at(10, 0, day_offset=1)
        first = c.post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(slot_start),
                "guestName": "Sam",
            },
        )
        assert first.status_code == 201

        conflict = c.post(
            "/api/bookings",
            json={
                "eventTypeId": "fifteen-minute-call",
                "slotStart": iso(slot_start),
                "guestName": "Alex",
            },
        )
        assert conflict.status_code == 409
        assert conflict.get_json()["error"]["code"] == "slot_occupied"

        fifteen_slots = c.get("/api/slots?eventTypeId=fifteen-minute-call").get_json()
        fifteen_starts = [slot["start"] for slot in fifteen_slots["availableSlots"]]
        assert iso(slot_start) not in fifteen_starts
        assert iso(slot_start + timedelta(minutes=15)) not in fifteen_starts

    def test_day_15_is_outside_window(self, client):
        response = client("default_types.yml").post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(utc_today_at(10, 0, day_offset=14)),
                "guestName": "Sam",
            },
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "slot_outside_window"

    def test_day_27_is_outside_window(self, client):
        response = client("default_types.yml").post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(utc_today_at(10, 0, day_offset=26)),
                "guestName": "Sam",
            },
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "slot_outside_window"

    def test_off_grid_start_is_slot_mismatch(self, client):
        response = client("default_types.yml").post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(utc_today_at(10, 17, day_offset=1)),
                "guestName": "Sam",
            },
        )
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "slot_mismatch"

    def test_missing_guest_name_is_validation_error(self, client):
        response = client("default_types.yml").post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(utc_today_at(10, 0, day_offset=1)),
            },
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "validation_error"
