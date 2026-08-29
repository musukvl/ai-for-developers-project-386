import type {
  BookingList,
  CreateEventTypeRequest,
  EventType,
  EventTypeList,
} from "../api/types";
import { apiClient } from "../api/client";

export function listEventTypes(): Promise<EventTypeList> {
  return apiClient.get<EventTypeList>("/event-types");
}

export function createEventType(body: CreateEventTypeRequest): Promise<EventType> {
  return apiClient.post<EventType>("/owner/event-types", body);
}

export function deleteEventType(eventTypeId: string): Promise<void> {
  return apiClient.del(`/owner/event-types/${encodeURIComponent(eventTypeId)}`);
}

export function listOwnerBookings(): Promise<BookingList> {
  return apiClient.get<BookingList>("/owner/bookings");
}

export function cancelBooking(bookingId: string): Promise<void> {
  return apiClient.del(`/owner/bookings/${encodeURIComponent(bookingId)}`);
}
