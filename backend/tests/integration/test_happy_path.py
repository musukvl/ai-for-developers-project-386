"""Happy-path integration: pick an event type, book a generated slot, owner sees it."""

from datetime import timedelta

from tests.integration.helpers import iso, utc_today_at


class TestHappyPath:
    def test_choose_type_book_slot_owner_sees_guest(self, client):
        c = client("default_types.yml")

        catalog = c.get("/api/event-types").get_json()["eventTypes"]
        assert {item["title"] for item in catalog} == {"15m call", "30m call"}

        slot_start = utc_today_at(10, 0, day_offset=1)
        booking = c.post(
            "/api/bookings",
            json={
                "eventTypeId": "thirty-minute-call",
                "slotStart": iso(slot_start),
                "guestName": "Sam",
            },
        )
        assert booking.status_code == 201

        thirty_response = c.get("/api/slots?eventTypeId=thirty-minute-call").get_json()
        thirty_slots = thirty_response["availableSlots"]
        thirty_starts = [slot["start"] for slot in thirty_slots]
        assert iso(slot_start) not in thirty_starts
        assert iso(slot_start - timedelta(minutes=30)) in thirty_starts
        assert iso(slot_start + timedelta(minutes=30)) in thirty_starts

        fifteen_slots = c.get("/api/slots?eventTypeId=fifteen-minute-call").get_json()[
            "availableSlots"
        ]
        fifteen_starts = [slot["start"] for slot in fifteen_slots]
        assert iso(slot_start) not in fifteen_starts
        assert iso(slot_start + timedelta(minutes=15)) not in fifteen_starts

        owner = c.get("/api/owner/bookings").get_json()["bookings"]
        assert len(owner) == 1
        assert owner[0]["guestName"] == "Sam"
        assert owner[0]["eventTypeTitle"] == "30m call"
        assert owner[0]["start"] == iso(slot_start)
