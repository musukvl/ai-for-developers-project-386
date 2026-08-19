"""End-to-end API walk-through of spec/use_cases/happy-path.md.

Enter name, create a calendar, publish availability, and have another user
book a slot. This is dataflow, so it belongs in integration tests rather
than unit tests.
"""

from datetime import timedelta

from .helpers import future_range, iso


class TestHappyPath:
    def test_enter_create_publish_book(self, client):
        c = client("empty.yml")

        # Enter Name: Alex is unknown, gets registered and normalized.
        enter_response = c.post("/api/users", json={"name": "Alex"})
        assert enter_response.status_code == 200
        assert enter_response.get_json() == {"name": "alex", "isNew": True, "hasCalendar": False}

        # Create Calendar: alex has no calendar yet, creates one named after them.
        create_response = c.post(
            "/api/calendars", json={"ownerId": "alex"}, headers={"X-User-Name": "alex"}
        )
        assert create_response.status_code == 201
        assert create_response.get_json()["calendarUrl"] == "/cal/alex"

        # Publish Availability: a one-hour range becomes two 30-minute slots.
        start, end = future_range(duration=timedelta(hours=1))
        availability_response = c.post(
            "/api/calendars/alex/availability",
            json={"start": iso(start), "end": iso(end)},
            headers={"X-User-Name": "alex"},
        )
        assert availability_response.status_code == 200
        published_slots = availability_response.get_json()["availableSlots"]
        assert [s["start"] for s in published_slots] == [
            iso(start),
            iso(start + timedelta(minutes=30)),
        ]

        # Book a Meeting: Sam enters their name in a separate tab and books the first slot.
        sam_enter_response = c.post("/api/users", json={"name": "Sam"})
        assert sam_enter_response.get_json() == {
            "name": "sam",
            "isNew": True,
            "hasCalendar": False,
        }

        visitor_view = c.get("/api/calendars/alex", headers={"X-User-Name": "sam"}).get_json()
        assert len(visitor_view["availableSlots"]) == 2
        assert visitor_view["myBookings"] == []

        booking_response = c.post(
            "/api/calendars/alex/bookings",
            json={"slotStart": iso(start)},
            headers={"X-User-Name": "sam"},
        )
        assert booking_response.status_code == 201
        booking = booking_response.get_json()
        assert booking["visitorName"] == "sam"
        assert booking["start"] == iso(start)

        # Result: the booked slot is gone from availability, the other remains.
        visitor_view_after = c.get(
            "/api/calendars/alex", headers={"X-User-Name": "sam"}
        ).get_json()
        assert [s["start"] for s in visitor_view_after["availableSlots"]] == [
            iso(start + timedelta(minutes=30))
        ]
        assert len(visitor_view_after["myBookings"]) == 1

        # The owner refreshes and sees the upcoming booking with the visitor's name.
        owner_view = c.get(
            "/api/calendars/alex/owner", headers={"X-User-Name": "alex"}
        ).get_json()
        assert len(owner_view["bookings"]) == 1
        assert owner_view["bookings"][0]["visitorName"] == "sam"
        assert owner_view["bookings"][0]["start"] == iso(start)

        # alex has one calendar; sam has none.
        assert c.post("/api/users", json={"name": "alex"}).get_json()["hasCalendar"] is True
        assert c.post("/api/users", json={"name": "sam"}).get_json()["hasCalendar"] is False
