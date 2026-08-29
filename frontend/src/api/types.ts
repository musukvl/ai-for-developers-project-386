export type ApiErrorCode =
  | "validation_error"
  | "not_found"
  | "conflict"
  | "slot_occupied"
  | "slot_outside_window"
  | "slot_mismatch"
  | "future_bookings_exist";

export interface EventType {
  id: string;
  title: string;
  description: string;
  durationMinutes: number;
}

export interface EventTypeList {
  eventTypes: EventType[];
}

export interface Slot {
  start: string;
  end: string;
}

export interface SlotList {
  eventTypeId: string;
  availableSlots: Slot[];
}

export interface Booking {
  id: string;
  eventTypeId: string;
  eventTypeTitle: string;
  start: string;
  end: string;
  guestName: string;
}

export interface BookingList {
  bookings: Booking[];
}

export interface CreateEventTypeRequest {
  id: string;
  title: string;
  description: string;
  durationMinutes: number;
}

export interface CreateBookingRequest {
  eventTypeId: string;
  slotStart: string;
  guestName: string;
}
