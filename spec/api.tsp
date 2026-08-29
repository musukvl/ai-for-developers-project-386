import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;

@service(#{ title: "Calls Calendar API" })
@route("/api")
namespace CallsCalendar;

enum ErrorCode {
  validation_error: "validation_error",
  not_found: "not_found",
  conflict: "conflict",
}

model ErrorDetail {
  code: ErrorCode;
  message: string;
}

model ErrorResponse {
  error: ErrorDetail;
}

@error
model BadRequest extends ErrorResponse {
  @statusCode
  statusCode: 400;
}

@error
model NotFound extends ErrorResponse {
  @statusCode
  statusCode: 404;
}

@error
model Conflict extends ErrorResponse {
  @statusCode
  statusCode: 409;
}

model Created {
  @statusCode
  statusCode: 201;
}

model NoContent {
  @statusCode
  statusCode: 204;
}

/**
 * Event type the guest picks before booking.
 * Default types are `fifteen-minute-call` (15m call) and `thirty-minute-call` (30m call).
 */
model EventType {
  id: string;
  title: string;
  description: string;
  durationMinutes: int32;
}

model EventTypeList {
  eventTypes: EventType[];
}

model CreateEventTypeRequest {
  id: string;
  title: string;
  description: string;
  durationMinutes: int32;
}

model Slot {
  start: utcDateTime;
  end: utcDateTime;
}

/** Generated free slots for one event type over the 14-day window. */
model SlotList {
  eventTypeId: string;
  availableSlots: Slot[];
}

model Booking {
  /** Opaque server-generated booking identifier. */
  id: string;
  eventTypeId: string;
  eventTypeTitle: string;
  start: utcDateTime;
  end: utcDateTime;
  /** Name the guest typed when confirming this slot. Not an account. */
  guestName: string;
}

model BookingList {
  bookings: Booking[];
}

model CreateBookingRequest {
  eventTypeId: string;
  slotStart: utcDateTime;
  guestName: string;
}

model CreateBookingResponse extends Created {
  id: string;
  eventTypeId: string;
  eventTypeTitle: string;
  start: utcDateTime;
  end: utcDateTime;
  guestName: string;
}

model HealthResponse {
  status: "ok";
  seedFile: string;
}

/** Lists event types for the public catalog. No login. */
@get
@route("/event-types")
op listEventTypes(): EventTypeList;

/** Owner creates an event type. Admin uses the predefined owner profile; no sign-in header. */
@post
@route("/owner/event-types")
op createEventType(
  @body body: CreateEventTypeRequest,
): EventType | BadRequest | Conflict;

/** Generated free slots for the selected event type in the 14-day window. */
@get
@route("/slots")
op listSlots(@query eventTypeId: string): SlotList | BadRequest | NotFound;

/** Guest books a generated slot. guestName is collected at confirm time, not from a session. */
@post
@route("/bookings")
op createBooking(
  @body body: CreateBookingRequest,
): CreateBookingResponse | BadRequest | NotFound | Conflict;

/** Owner upcoming meetings: all event types in one list. */
@get
@route("/owner/bookings")
op listOwnerBookings(): BookingList;

/** Owner cancels a booking. The interval becomes a free generated slot again. */
@delete
@route("/owner/bookings/{bookingId}")
op cancelBookingAsOwner(
  @path bookingId: string,
): NoContent | NotFound;

/** Readiness probe for the API and Docker image. */
@get
@route("/health")
op health(): HealthResponse;
