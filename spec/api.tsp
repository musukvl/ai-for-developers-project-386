import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;

@service(#{ title: "Calls Calendar API" })
@route("/api")
namespace CallsCalendar;

/**
 * A user name after trimming and lowercasing. It must match `[a-z0-9-]+`.
 */
@minLength(3)
@maxLength(64)
@pattern("^[a-z0-9-]+$")
scalar NormalizedUserName extends string;

/** Required on every endpoint except entering a name and the health check. */
model UserNameHeader {
  @header("X-User-Name")
  userName: NormalizedUserName;
}

enum ErrorCode {
  validation_error: "validation_error",
  name_mismatch: "name_mismatch",
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

model Slot {
  start: utcDateTime;
  end: utcDateTime;
}

model Booking {
  /** Opaque server-generated booking identifier. */
  id: string;
  start: utcDateTime;
  end: utcDateTime;
  visitorName: NormalizedUserName;
}

model VisitorCalendar {
  ownerId: NormalizedUserName;
  availableSlots: Slot[];
  /** Bookings belonging only to the user named in X-User-Name. */
  myBookings: Booking[];
}

model OwnerCalendar {
  ownerId: NormalizedUserName;
  availableSlots: Slot[];
  /** All upcoming bookings on this calendar. */
  bookings: Booking[];
}

model EnterNameRequest {
  /** The unnormalized name supplied on the start page. */
  name: string;
}

model EnterNameResponse {
  /** The normalized name the client stores and later sends as X-User-Name. */
  name: NormalizedUserName;
  isNew: boolean;
  hasCalendar: boolean;
}

model CalendarSummary {
  ownerId: NormalizedUserName;
}

model CalendarDirectory {
  /** Calendars sorted alphabetically by ownerId. */
  calendars: CalendarSummary[];
}

model CreateCalendarRequest {
  ownerId: NormalizedUserName;
}

model Created {
  @statusCode
  statusCode: 201;
}

model CreateCalendarResponse extends Created {
  ownerId: NormalizedUserName;
  calendarUrl: string;
}

model AvailabilityRange {
  start: utcDateTime;
  end: utcDateTime;
}

model AvailabilityResponse {
  /** The calendar's complete free-slot list after the change. */
  availableSlots: Slot[];
}

model CreateBookingRequest {
  slotStart: utcDateTime;
}

model CreateBookingResponse extends Created {
  id: string;
  start: utcDateTime;
  end: utcDateTime;
  visitorName: NormalizedUserName;
}

model NoContent {
  @statusCode
  statusCode: 204;
}

model HealthResponse {
  status: "ok";
  seedFile: string;
}

/** Registers a new user or returns the existing user's normalized identity. */
@post
@route("/users")
op enterName(@body body: EnterNameRequest): EnterNameResponse | BadRequest;

/** Lists all public calendars. */
@get
@route("/calendars")
op listCalendars(...UserNameHeader): CalendarDirectory | BadRequest;

/** Creates the current user's one public calendar. */
@post
@route("/calendars")
op createCalendar(
  ...UserNameHeader,
  @body body: CreateCalendarRequest,
): CreateCalendarResponse | BadRequest | Conflict;

/** Retrieves the full owner-management view for a calendar. */
@get
@route("/calendars/{ownerId}/owner")
op getOwnerCalendar(
  ...UserNameHeader,
  @path ownerId: NormalizedUserName,
): OwnerCalendar | BadRequest | NotFound;

/** Adds a UTC availability range and expands it into 30-minute slots. */
@post
@route("/calendars/{ownerId}/availability")
op addAvailability(
  ...UserNameHeader,
  @path ownerId: NormalizedUserName,
  @body body: AvailabilityRange,
): AvailabilityResponse | BadRequest | NotFound;

/** Removes one currently free 30-minute slot. */
@delete
@route("/calendars/{ownerId}/availability/{slotStart}")
op removeAvailabilitySlot(
  ...UserNameHeader,
  @path ownerId: NormalizedUserName,
  @path slotStart: utcDateTime,
): NoContent | BadRequest | NotFound | Conflict;

/** Cancels any upcoming booking on the current user's calendar. */
@delete
@route("/calendars/{ownerId}/owner/bookings/{bookingId}")
op cancelBookingAsOwner(
  ...UserNameHeader,
  @path ownerId: NormalizedUserName,
  @path bookingId: string,
): NoContent | BadRequest | NotFound;

/** Retrieves the public booking view for a calendar. */
@get
@route("/calendars/{ownerId}")
op getVisitorCalendar(
  ...UserNameHeader,
  @path ownerId: NormalizedUserName,
): VisitorCalendar | BadRequest | NotFound;

/** Atomically books one currently available 30-minute slot. */
@post
@route("/calendars/{ownerId}/bookings")
op createBooking(
  ...UserNameHeader,
  @path ownerId: NormalizedUserName,
  @body body: CreateBookingRequest,
): CreateBookingResponse | BadRequest | NotFound | Conflict;

/** Cancels the current user's own upcoming booking. */
@delete
@route("/calendars/{ownerId}/bookings/{bookingId}")
op cancelBookingAsVisitor(
  ...UserNameHeader,
  @path ownerId: NormalizedUserName,
  @path bookingId: string,
): NoContent | BadRequest | NotFound;

/** Readiness probe for the API and Docker image. */
@get
@route("/health")
op health(): HealthResponse;
