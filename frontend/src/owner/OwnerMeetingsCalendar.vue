<script setup lang="ts">
import { computed, ref, watch } from "vue";

import type { Booking } from "../api/types";
import {
  WEEKDAY_LABELS,
  buildMonthGrid,
  monthLabel,
  todayDateKey,
  type CalendarDay,
} from "../shared/calendarGrid";
import { dateKeyFromIso, formatSlotRange, formatTime } from "../shared/dateTime";

const props = defineProps<{
  bookings: Booking[];
}>();

const emit = defineEmits<{
  (event: "cancel", bookingId: string): void;
}>();

const today = todayDateKey();
const selectedDate = ref<string | null>(null);
const viewYear = ref(new Date().getUTCFullYear());
const viewMonth = ref(new Date().getUTCMonth());

const countsByDate = computed(() => {
  const counts = new Map<string, number>();
  for (const booking of props.bookings) {
    const dateKey = dateKeyFromIso(booking.start);
    counts.set(dateKey, (counts.get(dateKey) ?? 0) + 1);
  }
  return counts;
});

const bookingsByDate = computed(() => {
  const grouped = new Map<string, Booking[]>();
  for (const booking of props.bookings) {
    const dateKey = dateKeyFromIso(booking.start);
    const bucket = grouped.get(dateKey);
    if (bucket) {
      bucket.push(booking);
    } else {
      grouped.set(dateKey, [booking]);
    }
  }
  for (const bucket of grouped.values()) {
    bucket.sort((left, right) => left.start.localeCompare(right.start) || left.id.localeCompare(right.id));
  }
  return grouped;
});

const days = computed(() =>
  buildMonthGrid(viewYear.value, viewMonth.value, countsByDate.value, today)
);

const currentMonthLabel = computed(() => monthLabel(viewYear.value, viewMonth.value));

const selectedDateBookings = computed<Booking[]>(() => {
  if (!selectedDate.value) {
    return [];
  }
  return bookingsByDate.value.get(selectedDate.value) ?? [];
});

watch(
  () => props.bookings,
  (bookings) => {
    if (selectedDate.value && bookingsByDate.value.has(selectedDate.value)) {
      return;
    }
    const first = bookings[0];
    if (!first) {
      selectedDate.value = null;
      return;
    }
    selectedDate.value = dateKeyFromIso(first.start);
    const focus = new Date(first.start);
    viewYear.value = focus.getUTCFullYear();
    viewMonth.value = focus.getUTCMonth();
  },
  { immediate: true }
);

function isSelectable(day: CalendarDay): boolean {
  return day.slotCount > 0;
}

function selectDay(day: CalendarDay): void {
  if (!isSelectable(day)) {
    return;
  }
  selectedDate.value = day.dateKey;
}

function goToPreviousMonth(): void {
  if (viewMonth.value === 0) {
    viewMonth.value = 11;
    viewYear.value -= 1;
  } else {
    viewMonth.value -= 1;
  }
}

function goToNextMonth(): void {
  if (viewMonth.value === 11) {
    viewMonth.value = 0;
    viewYear.value += 1;
  } else {
    viewMonth.value += 1;
  }
}

function dayButtonClass(day: CalendarDay): string {
  const selected = selectedDate.value === day.dateKey;
  if (selected) {
    return "bg-indigo-600 text-white";
  }
  if (!day.isCurrentMonth) {
    return "text-slate-300";
  }
  if (day.slotCount > 0) {
    return "bg-indigo-50 text-slate-900 hover:bg-indigo-100";
  }
  if (day.isPast) {
    return "text-slate-400 bg-slate-100";
  }
  return "text-slate-400";
}

function dayAriaLabel(day: CalendarDay): string {
  if (day.slotCount === 1) {
    return `${day.dateKey}, 1 booked meeting`;
  }
  if (day.slotCount > 1) {
    return `${day.dateKey}, ${day.slotCount} booked meetings`;
  }
  return day.dateKey;
}

function cancelLabel(booking: Booking): string {
  return `Cancel meeting with ${booking.guestName} at ${formatTime(booking.start)}`;
}
</script>

<template>
  <div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
    <section>
      <div class="mb-3 flex items-center justify-between">
        <button
          type="button"
          class="rounded px-2 py-1 text-sm font-medium text-slate-700 hover:bg-slate-100"
          aria-label="Previous month"
          @click="goToPreviousMonth"
        >
          Previous
        </button>
        <h3 class="text-base font-semibold">{{ currentMonthLabel }}</h3>
        <button
          type="button"
          class="rounded px-2 py-1 text-sm font-medium text-slate-700 hover:bg-slate-100"
          aria-label="Next month"
          @click="goToNextMonth"
        >
          Next
        </button>
      </div>
      <div class="grid grid-cols-7 gap-1 text-center text-xs font-medium text-slate-500">
        <div v-for="label in WEEKDAY_LABELS" :key="label">{{ label }}</div>
      </div>
      <div class="mt-1 grid grid-cols-7 gap-1">
        <button
          v-for="day in days"
          :key="day.dateKey"
          type="button"
          :disabled="!isSelectable(day)"
          :aria-label="dayAriaLabel(day)"
          :aria-pressed="selectedDate === day.dateKey"
          :class="[
            'flex min-h-14 flex-col items-center justify-center rounded-md text-sm disabled:cursor-not-allowed',
            dayButtonClass(day),
          ]"
          @click="selectDay(day)"
        >
          <span>{{ day.dayNumber }}</span>
          <span v-if="day.slotCount > 0" class="text-[11px] leading-none">{{ day.slotCount }}</span>
        </button>
      </div>
    </section>

    <section class="rounded-lg border border-slate-200 bg-white p-4">
      <h3 class="text-sm font-semibold text-slate-700">Meetings on this day</h3>
      <p v-if="!selectedDate" class="mt-3 text-sm text-slate-500">Select a date to see booked meetings.</p>
      <p v-else-if="selectedDateBookings.length === 0" class="mt-3 text-sm text-slate-500">
        No booked meetings on this date.
      </p>
      <ul v-else class="mt-3 space-y-3">
        <li v-for="booking in selectedDateBookings" :key="booking.id" class="space-y-1">
          <p class="text-sm font-medium">{{ formatSlotRange(booking) }}</p>
          <p class="text-sm text-slate-600">{{ booking.eventTypeTitle }} · {{ booking.guestName }}</p>
          <button
            type="button"
            class="text-sm font-semibold text-red-700"
            :aria-label="cancelLabel(booking)"
            @click="emit('cancel', booking.id)"
          >
            Cancel
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>
