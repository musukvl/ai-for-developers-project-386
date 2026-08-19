# Calls Calendar API

## Conventions

- The API is served by Flask under `/api` and uses JSON request and response bodies.
- Owner and visitor are separate API contracts. Do not return a mixed calendar shape or branch owner and visitor behavior inside one endpoint. Shared storage is allowed; request handlers, serializers, and frontend modules stay split by role.
- All date-time values are UTC ISO 8601 timestamps with seconds, for example `2026-08-01T10:00:00Z`.
- The user enters a name on the start page, and the SPA sends it in the required `X-User-Name` request header. Where the name is kept is a frontend concern only: the SPA stores it in `sessionStorage`, so it is scoped to the browser tab. The backend has no session configuration and treats every request as identified solely by `X-User-Name`.
- User names are not authentication credentials. They provide lightweight identification for this educational, public application.
- User names are normalized before use: trimmed and lowercased. A normalized name must be 3 to 64 characters long and match `[a-z0-9-]+`. Every endpoint except `POST /api/users` and `GET /api/health` rejects a missing or non-conforming `X-User-Name` with `400 validation_error`. Normalization never rewrites characters beyond trimming and lowercasing, so `Sam Smith` normalizes to `sam smith` and is rejected rather than converted to `sam-smith`.
- A well-formed `X-User-Name` that is not yet known is accepted and registered on first use. There is no authentication, so requiring a prior `POST /api/users` call would add a failure mode without adding safety. `POST /api/users` exists so the start page can learn `isNew` and `hasCalendar`, not to gate the other endpoints.
- A calendar's `ownerId` is always the normalized user name of its owner, so a user has at most one calendar and it always lives at `/cal/{name}`.
- The role is decided in the frontend by comparing the entered name with the `{ownerId}` in the URL. There is no role or session endpoint. Whether the calendar exists is learned from the owner or visitor `GET` call the chosen module makes.
- A slot is exactly 30 minutes. Slot start times must fall on a 30-minute boundary.
- The rolling four-week horizon runs from the moment a request is handled to exactly 28 days later. Availability is accepted when every resulting slot starts no earlier than that moment and ends no later than 28 days after it.
- Time moves, so the horizon is re-evaluated on every request. A slot or booking whose start has passed is no longer returned by any `GET`, and it is no longer addressable: removing it, cancelling it, or booking it fails as if it were absent. Nothing is deleted from storage, the past is simply invisible. Slots at the far end of the horizon are never dropped, because a slot that was valid when it was added only gets closer as time passes.
- `availableSlots` is always sorted ascending by `start`. `bookings` and `myBookings` are sorted ascending by `start`, with ties broken by `id`, so clients never need to sort.
- Booking IDs are opaque, server-generated, globally unique strings. Clients must treat them as arbitrary text and never parse or construct them.
- The owner is not blocked from using the visitor API on their own calendar; the rule that they see the owner view is a frontend routing decision, not a server-side restriction.
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
- `name_mismatch` means the `X-User-Name` header does not equal the owner the request targets, so the caller asked for an owner operation on someone else's calendar. Both values come from the request itself, so no lookup is involved. There is no authentication in this application and therefore no `401` or `403` response: a client receiving `name_mismatch` must not clear the entered name, it should offer to enter the calendar owner's name instead.
- Checks run in a fixed order, and the first failure decides the response. This matters when several would fail at once, for instance a mistyped owner name on a calendar that does not exist:

  1. `X-User-Name` is present and conforms to the name rules, otherwise `400 validation_error`.
  2. For owner endpoints, the header equals the owner the request targets, otherwise `400 name_mismatch`. No storage is read, so a mismatch is reported even when the calendar does not exist.
  3. The calendar, slot, or booking named in the path exists and is not in the past, otherwise `404 not_found`. A `{ownerId}` that is not a conforming normalized name is `404 not_found`, because such a calendar can never exist.
  4. The request body parses as JSON and satisfies the endpoint's rules, otherwise `400 validation_error`. A malformed `{slotStart}` in a path is a lookup miss rather than a body error, so it is `404 not_found`.
  5. The operation is compatible with current state, otherwise `409 conflict`.

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
  "id": "9f1c7a3e4b8d4f2a9c6e1b0d5a7f3c82",
  "start": "2026-08-01T10:30:00Z",
  "end": "2026-08-01T11:00:00Z",
  "visitorName": "sam"
}
```

`id` is a UUID4 hex string. Seed data may pin readable IDs instead so tests can reference a booking by name; the API contract is the same either way, the value is opaque.

The examples below shorten it to `booking-id` for readability.

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

## Calendar Directory API

### List Calendars

`GET /api/calendars`

Returns every existing public calendar, sorted alphabetically by owner name. The
`X-User-Name` header is required, but any valid user can read the directory.
An empty directory returns `200 OK` with an empty `calendars` array.

Response: `200 OK`

```json
{
  "calendars": [
    {
      "ownerId": "alex"
    },
    {
      "ownerId": "blake"
    }
  ]
}
```

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

`ownerId` must equal the normalized `X-User-Name`; any other value is rejected with `400 name_mismatch`, the same code used when the owner is named in the path. A missing or non-string `ownerId` is `400 validation_error`.

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

`availableSlots` is the calendar's complete list of free slots after the range was added, not just the slots this request produced, so the client can replace its state in one step.

Both bounds must be 30-minute boundaries, the end must be after the start, and all resulting slots must be from now through the rolling four-week horizon. Existing available or booked slots in an overlapping range are retained once; adding an overlap succeeds without duplication and never disturbs a booking. Returns `400 name_mismatch` when the current user name is not `{ownerId}`, `404 not_found` when the calendar does not exist, and `400 validation_error` when a bound is missing, unparseable, off a 30-minute boundary, not after the start, or outside the horizon.

### Remove Availability Slot

`DELETE /api/calendars/{ownerId}/availability/{slotStart}`

Owner-only. `slotStart` is a URL-encoded UTC ISO 8601 timestamp, for example `2026-08-01T10%3A00%3A00Z`.

Response: `204 No Content`

Only an available slot can be removed. Removing a booked slot returns `409 conflict`; to remove that time the owner cancels the booking first, which frees the slot. Bookings remain valid when adjacent availability is removed. Returns `400 name_mismatch` when the current user name is not `{ownerId}`, and `404 not_found` when the calendar does not exist, when `{slotStart}` is not a parseable timestamp, or when no slot starts at that instant — including a slot that has already started, which is treated as absent.

### Cancel Booking as Owner

`DELETE /api/calendars/{ownerId}/owner/bookings/{bookingId}`

Owner-only. Cancels any booking on the calendar. The freed slot returns to `availableSlots` and can be booked again; to take the time off the calendar entirely, the owner removes the slot after cancelling.

Response: `204 No Content`

Returns `400 name_mismatch` when the current user name is not `{ownerId}`, and `404 not_found` when the calendar or booking does not exist or the booking has already started.

## Visitor API

### Get Visitor Calendar

`GET /api/calendars/{ownerId}`

Public in the sense that no ownership check is applied: any user may read any calendar. The `X-User-Name` header is still required, because `myBookings` is resolved from it. Returns `404 not_found` if the public calendar does not exist.

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

The server performs the availability check and slot reservation atomically. Returns `404 not_found` when the calendar does not exist, `400 validation_error` when `slotStart` is missing or unparseable, and `409 conflict` when no free slot starts at that instant — whether it was never published, was already booked, was removed by the owner, or has already started. Booking is the one place where an unbookable time is a conflict rather than a lookup miss, because the client is acting on a slot it just saw.

### Cancel Booking as Visitor

`DELETE /api/calendars/{ownerId}/bookings/{bookingId}`

Cancels a booking made by the current `X-User-Name`. The freed slot returns to `availableSlots` and can be booked again.

Response: `204 No Content`

Returns `404 not_found` when the calendar or booking does not exist, when the booking has already started, or when the booking was made by another user: the visitor API only ever exposes the caller's own bookings, so another user's booking ID is indistinguishable from a missing one.

## Health

### Health Check

`GET /api/health`

Readiness probe for the Docker image and for test harnesses waiting on the backend. Requires no `X-User-Name` header.

Response: `200 OK`

```json
{
  "status": "ok",
  "seedFile": "src/seed.yml"
}
```
