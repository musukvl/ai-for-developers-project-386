# Calls Calendar API

## Conventions

- The API is served by Flask under `/api` and uses JSON request and response bodies.
- Owner and visitor are separate API contracts. Do not return a mixed calendar shape or branch owner and visitor behavior inside one endpoint. Shared storage is allowed; request handlers, serializers, and frontend modules stay split by role.
- All date-time values are UTC ISO 8601 timestamps with seconds, for example `2026-08-01T10:00:00Z`.
- The user enters a name on the start page, and the SPA sends it in the required `X-User-Name` request header. Where the name is kept is a frontend concern only: the SPA stores it in `sessionStorage`, so it is scoped to the browser tab. The backend has no session configuration and treats every request as identified solely by `X-User-Name`.
- User names are not authentication credentials. They provide lightweight identification for this educational, public application.
- User names are normalized before use: trimmed and lowercased. A normalized name must be 3 to 64 characters long and match `[a-z0-9-]+`. Every endpoint except `POST /api/users` rejects a missing or non-conforming `X-User-Name` with `400 validation_error`.
- A calendar's `ownerId` is always the normalized user name of its owner, so a user has at most one calendar and it always lives at `/cal/{name}`.
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

- Error codes are `validation_error` (400), `name_mismatch` (400), `not_found` (404), and `conflict` (409).
- `name_mismatch` means the `X-User-Name` header does not equal the `{ownerId}` in the path, so the caller asked for an owner operation on someone else's calendar. Both values come from the request itself, so no lookup is involved. There is no authentication in this application and therefore no `401` or `403` response: a client receiving `name_mismatch` must not clear the entered name, it should offer to enter the calendar owner's name instead.

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
  "visitorName": "sam"
}
```

### Visitor Calendar

Public booking view. `myBookings` contains only bookings made by the current `X-User-Name`. Other visitors' names and meeting details are not included.

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
      "visitorName": "sam"
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
      "visitorName": "sam"
    }
  ]
}
```

## Users API

### Enter Name

`POST /api/users`

Registers a new user or signs in an existing one. The submitted name is normalized before lookup, so `Sam`, `sam`, and ` SAM ` are the same user. This is the only endpoint that does not require the `X-User-Name` header.

Request:

```json
{
  "name": "Sam"
}
```

Response: `200 OK`

```json
{
  "name": "sam",
  "isNew": false,
  "hasCalendar": true
}
```

`name` is the normalized name the SPA must store and send back as `X-User-Name`. `isNew` is `true` when the name was not yet known and has just been registered. `hasCalendar` is `true` when a calendar named after this user exists, letting the start page link straight to `/cal/{name}` instead of offering the create form. Returns `400 validation_error` when the normalized name does not satisfy the name rules.

## Session Role

`GET /api/calendars/{ownerId}/session`

Returns which SPA module the current user should mount for this calendar. This endpoint is a routing probe only. It does not return slots or bookings.

Response: `200 OK`

```json
{
  "role": "owner"
}
```

`role` is `owner` when the normalized `X-User-Name` equals `{ownerId}`, and `visitor` otherwise. Returns `404 not_found` if the public calendar does not exist.

## Owner API

### Create Calendar

`POST /api/calendars`

Creates one public calendar for the current user.

Request:

```json
{
  "ownerId": "alex"
}
```

`ownerId` must equal the normalized `X-User-Name`; any other value is rejected with `400 validation_error`.

Response: `201 Created`

```json
{
  "ownerId": "alex",
  "calendarUrl": "/cal/alex"
}
```

`calendarUrl` is both where the owner manages the calendar and the link shared with visitors: the SPA mounts the owner or visitor module by comparing the entered name with the calendar's `ownerId`. Returns `409 conflict` when the user already has a calendar.

### Get Owner Calendar

`GET /api/calendars/{ownerId}/owner`

Owner-only. Returns the owner calendar shape. Returns `400 name_mismatch` when the current user name is not `{ownerId}`, and `404 not_found` if the public calendar does not exist.

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

Both bounds must be 30-minute boundaries, the end must be after the start, and all resulting slots must be from now through the rolling four-week horizon. Existing available or booked slots in an overlapping range are retained once; adding an overlap succeeds without duplication. Returns `400 name_mismatch` when the current user name is not `{ownerId}`.

### Remove Availability Slot

`DELETE /api/calendars/{ownerId}/availability/{slotStart}`

Owner-only. `slotStart` is a URL-encoded UTC ISO 8601 timestamp, for example `2026-08-01T10%3A00%3A00Z`.

Response: `204 No Content`

Only an available slot can be removed. Removing a booked slot returns `409 conflict`; to remove that time the owner cancels the booking first, which frees the slot. Bookings remain valid when adjacent availability is removed. Returns `400 name_mismatch` when the current user name is not `{ownerId}`, and `404 not_found` when the calendar or slot is not available.

### Cancel Booking as Owner

`DELETE /api/calendars/{ownerId}/owner/bookings/{bookingId}`

Owner-only. Cancels any booking on the calendar. The freed slot returns to `availableSlots` and can be booked again; to take the time off the calendar entirely, the owner removes the slot after cancelling.

Response: `204 No Content`

Returns `400 name_mismatch` when the current user name is not `{ownerId}`, and `404 not_found` when the calendar or booking does not exist.

## Visitor API

### Get Visitor Calendar

`GET /api/calendars/{ownerId}`

Public. Returns the visitor calendar shape for any user. Returns `404 not_found` if the public calendar does not exist.

### Create Booking

`POST /api/calendars/{ownerId}/bookings`

Books an available slot for the current user. The booking's `visitorName` is the current `X-User-Name`, so no name is submitted in the body.

Request:

```json
{
  "slotStart": "2026-08-01T10:00:00Z"
}
```

Response: `201 Created`

```json
{
  "id": "booking-id",
  "start": "2026-08-01T10:00:00Z",
  "end": "2026-08-01T10:30:00Z",
  "visitorName": "sam"
}
```

The server performs the availability check and slot reservation atomically. If another request has already booked or removed the slot, this endpoint returns `409 conflict`.

### Cancel Booking as Visitor

`DELETE /api/calendars/{ownerId}/bookings/{bookingId}`

Cancels a booking made by the current `X-User-Name`. The freed slot returns to `availableSlots` and can be booked again.

Response: `204 No Content`

Returns `404 not_found` when the calendar or booking does not exist, or when the booking was made by another user: the visitor API only ever exposes the caller's own bookings, so another user's booking ID is indistinguishable from a missing one.
