export const WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;

export const WINDOW_DAYS = 14;

export interface CalendarDay {
  dateKey: string;
  dayNumber: number;
  isCurrentMonth: boolean;
  isPast: boolean;
  isOutsideWindow: boolean;
  slotCount: number;
}

export function toDateKey(date: Date): string {
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const day = String(date.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function todayDateKey(): string {
  return toDateKey(new Date());
}

export function windowLastDateKey(todayKey: string): string {
  const date = new Date(`${todayKey}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + (WINDOW_DAYS - 1));
  return toDateKey(date);
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
  const lastWindowKey = windowLastDateKey(todayKey);
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
      isOutsideWindow: dateKey > lastWindowKey,
      slotCount: slotCountsByDate.get(dateKey) ?? 0,
    });
  }
  return days;
}
