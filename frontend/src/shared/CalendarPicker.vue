<script setup lang="ts">
import { computed, ref } from "vue";

import type { Slot } from "../api/types";
import {
  WEEKDAY_LABELS,
  buildMonthGrid,
  monthLabel,
  todayDateKey,
  type CalendarDay,
} from "./calendarGrid";
import { dateKeyFromIso, formatSlotRange } from "./dateTime";

const props = defineProps<{
  availableSlots: Slot[];
  modelValue: string | null;
  actionPendingId?: string | null;
}>();

const emit = defineEmits<{
  (event: "update:modelValue", value: string | null): void;
  (event: "book", slot: Slot): void;
}>();

const today = todayDateKey();
const initialFocusDate = props.modelValue
  ? new Date(`${props.modelValue}T00:00:00Z`)
  : new Date();
const viewYear = ref(initialFocusDate.getUTCFullYear());
const viewMonth = ref(initialFocusDate.getUTCMonth());

const slotsByDate = computed(() => {
  const map = new Map<string, Slot[]>();
  for (const slot of props.availableSlots) {
    const dateKey = dateKeyFromIso(slot.start);
    const bucket = map.get(dateKey);
    if (bucket) {
      bucket.push(slot);
    } else {
      map.set(dateKey, [slot]);
    }
  }
  return map;
});

const slotCountsByDate = computed(() => {
  const counts = new Map<string, number>();
  for (const [dateKey, slots] of slotsByDate.value) {
    counts.set(dateKey, slots.length);
  }
  return counts;
});

const days = computed(() =>
  buildMonthGrid(viewYear.value, viewMonth.value, slotCountsByDate.value, today)
);

const currentMonthLabel = computed(() => monthLabel(viewYear.value, viewMonth.value));

const selectedDateSlots = computed<Slot[]>(() => {
  if (!props.modelValue) {
    return [];
  }
  return [...(slotsByDate.value.get(props.modelValue) ?? [])].sort((left, right) =>
    left.start.localeCompare(right.start)
  );
});

function isSelectable(day: CalendarDay): boolean {
  return !day.isPast && !day.isOutsideWindow && day.slotCount > 0;
}

function selectDay(day: CalendarDay): void {
  if (!isSelectable(day)) {
    return;
  }
  emit("update:modelValue", day.dateKey);
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
  const selected = props.modelValue === day.dateKey;
  if (selected) {
    return "bg-sky-600 text-white";
  }
  if (!day.isCurrentMonth) {
    return "text-slate-300";
  }
  if (day.isPast || day.isOutsideWindow) {
    return "text-slate-400 bg-slate-100";
  }
  if (day.slotCount > 0) {
    return "bg-sky-50 text-slate-900 hover:bg-sky-100";
  }
  return "text-slate-400";
}

function dayAriaLabel(day: CalendarDay): string {
  const base = day.dateKey;
  if (day.slotCount > 0) {
    return `${base}, ${day.slotCount} available slots`;
  }
  return base;
}
</script>

<template>
  <div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_16rem]">
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
        <h2 class="text-base font-semibold">{{ currentMonthLabel }}</h2>
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
          :aria-pressed="modelValue === day.dateKey"
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
      <h3 class="text-sm font-semibold text-slate-700">Available times</h3>
      <p v-if="!modelValue" class="mt-3 text-sm text-slate-500">Select a date to see open slots.</p>
      <p v-else-if="selectedDateSlots.length === 0" class="mt-3 text-sm text-slate-500">
        No available slots on this date.
      </p>
      <ul v-else class="mt-3 space-y-2">
        <li
          v-for="slot in selectedDateSlots"
          :key="slot.start"
          class="flex items-center justify-between gap-2"
        >
          <span>{{ formatSlotRange(slot) }}</span>
          <button
            type="button"
            class="text-sm font-semibold text-sky-600 hover:text-sky-500 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="actionPendingId === slot.start"
            :aria-label="`Book ${formatSlotRange(slot)}`"
            @click="emit('book', slot)"
          >
            Book
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>
