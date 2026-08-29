# Calls Calendar API

`spec/api.tsp` is the source of truth for this contract. Keep this file in sync with the TypeSpec. The frontend and backend implement against the contract, not against each other.

## Conventions

- The API is served by Flask under `/api` and uses JSON request and response bodies.
- There is no authentication, no `X-User-Name` header, and no user-registration endpoint. The owner is a predefined profile used by default on owner routes. Guests call public routes without an account.
- Owner and guest are separate API surfaces. Do not return a mixed calendar shape or branch owner and guest behavior inside one endpoint. Shared storage is allowed; request handlers, serializers, and frontend modules stay split by role.
- All date-time values are UTC ISO 8601 timestamps with seconds, for example `2026-08-01T10:00:00Z`.
- A slot length is the selected event type's duration in minutes. Slot start times fall on that duration's grid from `00:00` UTC.
- The owner does not publish availability. The backend generates free slots for each UTC calendar day from today through today+13. A slot must start and end on the same UTC date. A slot or booking whose start has passed is not returned and is not addressable.
- A booking occupies its clock interval for every event type. Two bookings cannot overlap, even for different event types.
- Time moves, so the 14-day window is re-evaluated on every request. Nothing is deleted from storage; the past is simply invisible.
- `availableSlots` is always sorted ascending by `start`. `bookings` are sorted ascending by `start`, with ties broken by `id`, so clients never need to sort.
- Booking IDs are opaque, server-generated, globally unique strings. Clients must treat them as arbitrary text and never parse or construct them.
- `guestName` is the display name the guest types when confirming a slot. It is stored on that booking only. It is not an account, it is not sent as a header, and it is not remembered across pages.
- All error responses have the following shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The selected slot is already booked."
  }
}
```

- Error codes are `validation_error` (400), `not_found` (404), and `conflict` (409). There is no `name_mismatch`, `401`, or `403`.
- Checks run in a fixed order, and the first failure decides the response:

  1. The request body or required query parses and satisfies the endpoint's rules, otherwise `400 validation_error`.
  2. The event type or booking named in the request exists and is not in the past, otherwise `404 not_found`.
  3. The operation is compatible with current state, otherwise `409 conflict`.

## Data Shapes

### EventType

```json
{
  "id": "thirty-minute-call",
  "title": "30m call",
  "description": "A standard call.",
  "durationMinutes": 30
}
```

`id`, `title`, `description`, and `durationMinutes` are set by the owner on create. `durationMinutes` is an integer of at least 1. Default seeded types are `fifteen-minute-call` (`15m call`, 15) and `thirty-minute-call` (`30m call`, 30).

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
  "eventTypeId": "thirty-minute-call",
  "eventTypeTitle": "30m call",
  "start": "2026-08-01T10:30:00Z",
  "end": "2026-08-01T11:00:00Z",
  "guestName": "Sam"
}
```

`id` is a UUID4 hex string. Seed data may pin readable IDs instead so tests can reference a booking by name; the API contract is the same either way, the value is opaque.

The examples below shorten it to `booking-id` for readability.

`guestName` is the name collected on the booking form. It is not normalized to a user id.

## Guest API

Public. No login header.

### List Event Types

`GET /api/event-types`

Returns the catalog the guest sees before picking a type: title, description, and duration.

Response: `200 OK`

```json
{
  "eventTypes": [
    {
      "id": "fifteen-minute-call",
      "title": "15m call",
      "description": "A short call.",
      "durationMinutes": 15
    },
    {
      "id": "thirty-minute-call",
      "title": "30m call",
      "description": "A standard call.",
      "durationMinutes": 30
    }
  ]
}
```

### List Slots

`GET /api/slots?eventTypeId={eventTypeId}`

Returns generated free slots for that event type over the 14-day window. Slots are not stored availability.

Response: `200 OK`

```json
{
  "eventTypeId": "thirty-minute-call",
  "availableSlots": [
    {
      "start": "2026-08-01T10:00:00Z",
      "end": "2026-08-01T10:30:00Z"
    }
  ]
}
```

Returns `400 validation_error` when `eventTypeId` is missing, and `404 not_found` when the event type does not exist.

### Create Booking

`POST /api/bookings`

Books a generated free slot. The guest name is submitted in the body at confirm time.

Request:

```json
{
  "eventTypeId": "thirty-minute-call",
  "slotStart": "2026-08-01T10:00:00Z",
  "guestName": "Sam"
}
```

Response: `201 Created`

```json
{
  "id": "booking-id",
  "eventTypeId": "thirty-minute-call",
  "eventTypeTitle": "30m call",
  "start": "2026-08-01T10:00:00Z",
  "end": "2026-08-01T10:30:00Z",
  "guestName": "Sam"
}
```

`guestName` must be a non-empty string after trimming. It is stored on the booking as given (after trim) so the owner's upcoming list can show who is coming.

The server generates the slot grid for `eventTypeId`, checks occupancy, and reserves the slot atomically. Returns `404 not_found` when the event type does not exist, `400 validation_error` when `slotStart` or `guestName` is missing or unparseable, and `409 conflict` when that clock time is not a free generated slot — whether it was already booked, overlaps another event type's booking, is not on the duration grid, or has already started.

## Owner API

Admin routes for the predefined owner profile. No sign-in header.

### Create Event Type

`POST /api/owner/event-types`

Request:

```json
{
  "id": "strategy-session",
  "title": "Strategy session",
  "description": "Discuss the project roadmap.",
  "durationMinutes": 30
}
```

Response: `200 OK` with the created `EventType`.

Returns `400 validation_error` when a field is missing, `durationMinutes` is less than 1, or `id` is empty. Returns `409 conflict` when an event type with that `id` already exists.

### List Owner Bookings

`GET /api/owner/bookings`

Upcoming bookings of every event type in one list, including `guestName` and event type.

Response: `200 OK`

```json
{
  "bookings": [
    {
      "id": "booking-id",
      "eventTypeId": "thirty-minute-call",
      "eventTypeTitle": "30m call",
      "start": "2026-08-01T10:00:00Z",
      "end": "2026-08-01T10:30:00Z",
      "guestName": "Sam"
    }
  ]
}
```

Past bookings are omitted.

### Cancel Booking as Owner

`DELETE /api/owner/bookings/{bookingId}`

Cancels any upcoming booking. The freed interval returns to the generated free-slot list and can be booked again.

Response: `204 No Content`

Returns `404 not_found` when the booking does not exist or the booking has already started.

## Health

### Health Check

`GET /api/health`

Readiness probe for the Docker image and for test harnesses waiting on the backend.

Response: `200 OK`

```json
{
  "status": "ok",
  "seedFile": "src/seed.yml"
}
```
