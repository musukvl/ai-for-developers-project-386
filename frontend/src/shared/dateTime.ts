/**
 * UTC date/time formatting shared by the owner and visitor modules.
 *
 * All values from the API are UTC ISO 8601 timestamps; the `UTC` suffix is
 * never shown, and every date/time is read via the `getUTC*` accessors so
 * the browser's local timezone never leaks into the display.
 */

import type { Slot } from "../api/types";

function pad(value: number): string {
  return String(value).padStart(2, "0");
}

export function formatTime(iso: string): string {
  const date = new Date(iso);
  return `${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`;
}

export function formatSlotRange(slot: Slot): string {
  return `${formatTime(slot.start)}\u2013${formatTime(slot.end)}`;
}

export function formatBookingDateTime(iso: string): string {
  const date = new Date(iso);
  const y = date.getUTCFullYear();
  const m = pad(date.getUTCMonth() + 1);
  const d = pad(date.getUTCDate());
  return `${y}.${m}.${d} ${formatTime(iso)}`;
}

export function dateKeyFromIso(iso: string): string {
  return iso.slice(0, 10);
}
