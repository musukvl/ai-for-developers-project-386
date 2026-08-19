/** Month-grid math for the shared calendar picker, entirely in UTC. */

export interface CalendarDay {
  dateKey: string;
  dayNumber: number;
  isCurrentMonth: boolean;
  isPast: boolean;
  slotCount: number;
}

export const WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function toDateKey(date: Date): string {
  const y = date.getUTCFullYear();
  const m = String(date.getUTCMonth() + 1).padStart(2, "0");
  const d = String(date.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function todayDateKey(): string {
  return toDateKey(new Date());
}

export function monthLabel(year: number, month: number): string {
  return new Date(Date.UTC(year, month, 1)).toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
}

/** Builds a fixed 6-week (42-cell) Monday-first grid covering `month` of `year`. */
export function buildMonthGrid(
  year: number,
  month: number,
  slotCountsByDate: Map<string, number>,
  todayKey: string
): CalendarDay[] {
  const firstOfMonth = new Date(Date.UTC(year, month, 1));
  const firstWeekdayMondayBased = (firstOfMonth.getUTCDay() + 6) % 7;
  const gridStart = new Date(Date.UTC(year, month, 1 - firstWeekdayMondayBased));

  const days: CalendarDay[] = [];
  for (let offset = 0; offset < 42; offset += 1) {
    const current = new Date(gridStart);
    current.setUTCDate(gridStart.getUTCDate() + offset);
    const dateKey = toDateKey(current);
    days.push({
      dateKey,
      dayNumber: current.getUTCDate(),
      isCurrentMonth: current.getUTCMonth() === month,
      isPast: dateKey < todayKey,
      slotCount: slotCountsByDate.get(dateKey) ?? 0,
    });
  }
  return days;
}
