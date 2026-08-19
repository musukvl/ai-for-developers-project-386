/** Owner API calls. Never imported by the visitor module. */

import { apiClient } from "../api/client";
import type { CreateCalendarResult, OwnerCalendar, Slot } from "../api/types";

export function createCalendar(ownerId: string): Promise<CreateCalendarResult> {
  return apiClient.post<CreateCalendarResult>("/calendars", { ownerId });
}

export function getOwnerCalendar(ownerId: string): Promise<OwnerCalendar> {
  return apiClient.get<OwnerCalendar>(`/calendars/${encodeURIComponent(ownerId)}/owner`);
}

export function addAvailability(
  ownerId: string,
  start: string,
  end: string
): Promise<{ availableSlots: Slot[] }> {
  return apiClient.post<{ availableSlots: Slot[] }>(
    `/calendars/${encodeURIComponent(ownerId)}/availability`,
    { start, end }
  );
}

export function removeAvailabilitySlot(ownerId: string, slotStart: string): Promise<void> {
  return apiClient.del(
    `/calendars/${encodeURIComponent(ownerId)}/availability/${encodeURIComponent(slotStart)}`
  );
}

export function cancelBookingAsOwner(ownerId: string, bookingId: string): Promise<void> {
  return apiClient.del(
    `/calendars/${encodeURIComponent(ownerId)}/owner/bookings/${encodeURIComponent(bookingId)}`
  );
}
