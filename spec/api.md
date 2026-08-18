# Calls Calendar API

## Conventions

- The API is served by Flask under `/api` and uses JSON request and response bodies.
- Owner and visitor are separate API contracts. Do not return a mixed calendar shape or branch owner and visitor behavior inside one endpoint. Shared storage is allowed; request handlers, serializers, and frontend modules stay split by role.
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

### Slot

```json
{
  "start": "2026-08-01T10:00:00Z",
  "end": "2026-08-01T10:30:00Z"
}
```

### Booking

```json
{
  "id": "booking-id",
  "start": "2026-08-01T10:30:00Z",
  "end": "2026-08-01T11:00:00Z",
  "visitorName": "Sam"
}
```

### Visitor Calendar

Public booking view. `myBookings` contains only bookings created by the current `X-Session-ID`. Other visitors' names and meeting details are not included.

```json
{
  "ownerId": "alex",
  "availableSlots": [
    {
      "start": "2026-08-01T10:00:00Z",
      "end": "2026-08-01T10:30:00Z"
    }
  ],
  "myBookings": [
    {
      "id": "booking-id",
      "start": "2026-08-01T10:30:00Z",
      "end": "2026-08-01T11:00:00Z",
      "visitorName": "Sam"
    }
  ]
}
```

### Owner Calendar

Owner management view. `bookings` contains all upcoming bookings for the calendar.

```json
{
  "ownerId": "alex",
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
      "visitorName": "Sam"
    }
  ]
}
```

## Session Role

`GET /api/calendars/{ownerId}/session`

Returns which SPA module the current session should mount. This endpoint is a routing probe only. It does not return slots or bookings.

Response: `200 OK`

```json
{
  "role": "owner"
}
```

`role` is `owner` when `X-Session-ID` matches the session that created the calendar, and `visitor` otherwise. Returns `404 not_found` if the public calendar does not exist.

## Owner API

### Create Calendar

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
  "ownerUrl": "/cal/alex/owner",
  "publicUrl": "/cal/alex"
}
```

The SPA should open `ownerUrl`. `publicUrl` is the link the owner shares with visitors. Returns `409 conflict` when a calendar with the owner ID already exists. A session that already owns a calendar also receives `409 conflict`.

### Get Owner Calendar

`GET /api/calendars/{ownerId}/owner`

Owner-only. Returns the owner calendar shape. Returns `403 unauthorized` when the current session is not the calendar owner, and `404 not_found` if the public calendar does not exist.

### Add Availability

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

Both bounds must be 30-minute boundaries, the end must be after the start, and all resulting slots must be from now through the rolling four-week horizon. Existing available or booked slots in an overlapping range are retained once; adding an overlap succeeds without duplication. Returns `403 unauthorized` when the current session is not the calendar owner.

### Remove Availability Slot

`DELETE /api/calendars/{ownerId}/availability/{slotStart}`

Owner-only. `slotStart` is a URL-encoded UTC ISO 8601 timestamp, for example `2026-08-01T10%3A00%3A00Z`.

Response: `204 No Content`

Only an available slot can be removed. Removing a booked slot returns `409 conflict`; bookings remain valid even if adjacent availability has been removed. Returns `403 unauthorized` when the current session is not the calendar owner, and `404 not_found` when the calendar or slot is not available.

### Cancel Booking as Owner

`DELETE /api/calendars/{ownerId}/owner/bookings/{bookingId}`

Owner-only. Cancels any booking on the calendar.

Response: `204 No Content`

Returns `403 unauthorized` when the current session is not the calendar owner, and `404 not_found` when the calendar or booking does not exist.

## Visitor API

### Get Visitor Calendar

`GET /api/calendars/{ownerId}`

Public. Returns the visitor calendar shape for any session. Returns `404 not_found` if the public calendar does not exist.

### Create Booking

`POST /api/calendars/{ownerId}/bookings`

Books an available slot for the requesting visitor session.

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
  "visitorName": "Sam"
}
```

The server performs the availability check and slot reservation atomically. If another request has already booked or removed the slot, this endpoint returns `409 conflict`.

### Cancel Booking as Visitor

`DELETE /api/calendars/{ownerId}/bookings/{bookingId}`

Cancels a booking created by the current `X-Session-ID`.

Response: `204 No Content`

Returns `403 unauthorized` when the current session did not create the booking, and `404 not_found` when the calendar or booking does not exist.
