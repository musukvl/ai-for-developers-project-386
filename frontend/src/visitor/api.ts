/** Visitor API calls. Never imported by the owner module. */

import { apiClient } from "../api/client";
import type { Booking, VisitorCalendar } from "../api/types";

export function getVisitorCalendar(ownerId: string): Promise<VisitorCalendar> {
  return apiClient.get<VisitorCalendar>(`/calendars/${encodeURIComponent(ownerId)}`);
}

export function createBooking(ownerId: string, slotStart: string): Promise<Booking> {
  return apiClient.post<Booking>(`/calendars/${encodeURIComponent(ownerId)}/bookings`, { slotStart });
}

export function cancelBookingAsVisitor(ownerId: string, bookingId: string): Promise<void> {
  return apiClient.del(
    `/calendars/${encodeURIComponent(ownerId)}/bookings/${encodeURIComponent(bookingId)}`
  );
}
