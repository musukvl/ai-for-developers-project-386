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
  const year = date.getUTCFullYear();
  const month = pad(date.getUTCMonth() + 1);
  const day = pad(date.getUTCDate());
  return `${year}.${month}.${day} ${formatTime(iso)}`;
}

export function dateKeyFromIso(iso: string): string {
  return iso.slice(0, 10);
}
