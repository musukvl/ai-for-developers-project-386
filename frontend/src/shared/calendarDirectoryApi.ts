/** Neutral API call used by the calendar directory shared by both roles. */

import { apiClient } from "../api/client";
import type { CalendarDirectory } from "../api/types";

export function getCalendarDirectory(): Promise<CalendarDirectory> {
  return apiClient.get<CalendarDirectory>("/calendars");
}
