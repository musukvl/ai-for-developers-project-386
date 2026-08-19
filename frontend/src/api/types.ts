/** JSON shapes exchanged with the backend, per spec/api.md. */

export interface Slot {
  start: string;
  end: string;
}

export interface Booking {
  id: string;
  start: string;
  end: string;
  visitorName: string;
}

export interface VisitorCalendar {
  ownerId: string;
  availableSlots: Slot[];
  myBookings: Booking[];
}

export interface OwnerCalendar {
  ownerId: string;
  availableSlots: Slot[];
  bookings: Booking[];
}

export interface EnterNameResult {
  name: string;
  isNew: boolean;
  hasCalendar: boolean;
}

export interface CreateCalendarResult {
  ownerId: string;
  calendarUrl: string;
}
