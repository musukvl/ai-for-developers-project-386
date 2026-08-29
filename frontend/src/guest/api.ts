import type { Booking, CreateBookingRequest, EventTypeList, SlotList } from "../api/types";
import { apiClient } from "../api/client";

export function listEventTypes(): Promise<EventTypeList> {
  return apiClient.get<EventTypeList>("/event-types");
}

export function listSlots(eventTypeId: string): Promise<SlotList> {
  const query = new URLSearchParams({ eventTypeId });
  return apiClient.get<SlotList>(`/slots?${query.toString()}`);
}

export function createBooking(body: CreateBookingRequest): Promise<Booking> {
  return apiClient.post<Booking>("/bookings", body);
}
