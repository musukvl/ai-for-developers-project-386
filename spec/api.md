# Calls Calendar API

## Conventions

- The API is served by Flask under `/api` and uses JSON request and response bodies.
- All date-time values are UTC ISO 8601 timestamps with seconds, for example `2026-08-01T10:00:00Z`.
- Each SPA installation generates an opaque session ID and sends it in the required `X-Session-ID` request header. The frontend stores the ID in `sessionStorage` when built with `VITE_SESSION_MODE=tab`, or in `localStorage` when built with `VITE_SESSION_MODE=browser`.
- Session IDs are not authentication credentials. They provide lightweight ownership identification for this educational, public application.
- Calendar owner IDs must be unique, 3 to 64 characters long, and match `[a-z0-9-]+`.
- A slot is exactly 30 minutes. Slot start times must fall on a 30-minute boundary.
- All error responses have the following shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The availability end must be after its start."
  }
}
```

- Error codes are `validation_error` (400), `unauthorized` (403), `not_found` (404), and `conflict` (409).

## Data Shapes

### Calendar

```json
{
  "ownerId": "alex",
  "isOwner": true,
  "availableSlots": [
    {
      "start": "2026-08-01T10:00:00Z",
      "end": "2026-08-01T10:30:00Z"
    }
  ],
  "bookings": [
    {
      "id": "booking-id",
      "start": "2026-08-01T10:30:00Z",
      "end": "2026-08-01T11:00:00Z",
      "visitorName": "Sam",
      "isMine": false
    }
  ]
}
```

`bookings` contains all upcoming bookings for the owner. Visitors receive only bookings made by their current session, so other visitors' names and meeting details are not exposed.

## Create Calendar

`POST /api/calendars`

Creates one public calendar for the owner session.

Request:

```json
{
  "ownerId": "alex"
}
```

Response: `201 Created`

```json
{
  "ownerId": "alex",
  "calendarUrl": "/cal/alex"
}
```

Returns `409 conflict` when a calendar with the owner ID already exists. A session that already owns a calendar also receives `409 conflict`.

## Get Calendar

`GET /api/calendars/{ownerId}`

Returns the calendar shape above. `isOwner` is true only when the `X-Session-ID` matches the session that created the calendar. Returns `404 not_found` if the public calendar does not exist.

## Add Availability

`POST /api/calendars/{ownerId}/availability`

Owner-only. Adds a one-off availability range and expands it to 30-minute slots.

Request:

```json
{
  "start": "2026-08-01T10:00:00Z",
  "end": "2026-08-01T11:00:00Z"
}
```

Response: `200 OK`

```json
{
  "availableSlots": [
    {
      "start": "2026-08-01T10:00:00Z",
      "end": "2026-08-01T10:30:00Z"
    },
    {
      "start": "2026-08-01T10:30:00Z",
      "end": "2026-08-01T11:00:00Z"
    }
  ]
}
```

Both bounds must be 30-minute boundaries, the end must be after the start, and all resulting slots must be from now through the rolling four-week horizon. Existing available or booked slots in an overlapping range are retained once; adding an overlap succeeds without duplication.

## Remove Availability Slot

`DELETE /api/calendars/{ownerId}/availability/{slotStart}`

Owner-only. `slotStart` is a URL-encoded UTC ISO 8601 timestamp, for example `2026-08-01T10%3A00%3A00Z`.

Response: `204 No Content`

Only an available slot can be removed. Removing a booked slot returns `409 conflict`; bookings remain valid even if adjacent availability has been removed. Returns `404 not_found` when the slot is not available.

## Create Booking

`POST /api/calendars/{ownerId}/bookings`

Books an available slot for the requesting session.

Request:

```json
{
  "slotStart": "2026-08-01T10:00:00Z",
  "visitorName": "Sam"
}
```

`visitorName` is required and must contain 1 to 100 non-whitespace characters.

Response: `201 Created`

```json
{
  "id": "booking-id",
  "start": "2026-08-01T10:00:00Z",
  "end": "2026-08-01T10:30:00Z",
  "visitorName": "Sam",
  "isMine": true
}
```

The server performs the availability check and slot reservation atomically. If another request has already booked or removed the slot, this endpoint returns `409 conflict`.

## Cancel Booking

`DELETE /api/calendars/{ownerId}/bookings/{bookingId}`

The calendar owner may cancel any booking. A visitor may cancel only a booking created by the current `X-Session-ID`.

Response: `204 No Content`

Returns `403 unauthorized` when the current session is neither the owner nor the booking visitor, and `404 not_found` when the calendar or booking does not exist.
