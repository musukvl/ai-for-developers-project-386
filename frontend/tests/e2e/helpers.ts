/** Small helper for building horizon-safe, UTC-relative dates in e2e specs. */

export function futureDateKey(daysFromNow: number): string {
  const date = new Date();
  date.setUTCDate(date.getUTCDate() + daysFromNow);
  return date.toISOString().slice(0, 10);
}
