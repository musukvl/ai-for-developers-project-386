<script setup lang="ts">
/**
 * Shared monthly calendar and slot-picker used by both the owner and visitor
 * modules. Role differences (which days are selectable, the slot action
 * label) are passed in as props; this component never imports owner or
 * visitor code.
 */
import { computed, ref } from "vue";

import type { Slot } from "../api/types";
import { type CalendarDay, WEEKDAY_LABELS, buildMonthGrid, monthLabel, todayDateKey } from "./calendarGrid";
import { dateKeyFromIso, formatSlotRange } from "./dateTime";

const props = defineProps<{
  availableSlots: Slot[];
  mode: "owner" | "visitor";
  modelValue: string | null;
  actionLabel: string;
  actionPendingId?: string | null;
}>();

const emit = defineEmits<{
  (event: "update:modelValue", value: string | null): void;
  (event: "slotAction", slot: Slot): void;
}>();

const today = todayDateKey();

const initialFocusDate = props.modelValue ? new Date(`${props.modelValue}T00:00:00Z`) : new Date();
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
  return [...(slotsByDate.value.get(props.modelValue) ?? [])].sort((a, b) =>
    a.start.localeCompare(b.start)
  );
});

function isSelectable(day: CalendarDay): boolean {
  if (day.isPast) {
    return false;
  }
  return props.mode === "owner" ? true : day.slotCount > 0;
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

function dayAriaLabel(day: CalendarDay): string {
  if (day.slotCount === 0) {
    return day.dateKey;
  }
  return `${day.dateKey}, ${day.slotCount} available slot${day.slotCount === 1 ? "" : "s"}`;
}

/** A single, mutually-exclusive class string per day so disabled/past/outside-month
 * dates never fight with the "current month" text color for the same CSS property. */
function dayClasses(day: CalendarDay): string {
  if (props.modelValue === day.dateKey) {
    return "bg-sky-600 text-white hover:bg-sky-600";
  }
  if (day.isPast) {
    return "cursor-not-allowed text-slate-300 opacity-60";
  }
  if (!isSelectable(day)) {
    return "cursor-not-allowed text-slate-300";
  }
  if (!day.isCurrentMonth) {
    return "cursor-pointer text-slate-400 hover:bg-sky-50";
  }
  return "cursor-pointer text-slate-900 hover:bg-sky-50";
}
</script>

<template>
  <div class="space-y-4">
    <div class="rounded-lg border border-slate-200 bg-white p-4">
      <div class="mb-3 flex items-center justify-between">
        <button
          type="button"
          aria-label="Previous month"
          class="rounded-md px-2 py-1 text-lg text-slate-600 hover:bg-slate-100"
          @click="goToPreviousMonth"
        >
          &lsaquo;
        </button>
        <p class="text-sm font-semibold text-slate-800">{{ currentMonthLabel }}</p>
        <button
          type="button"
          aria-label="Next month"
          class="rounded-md px-2 py-1 text-lg text-slate-600 hover:bg-slate-100"
          @click="goToNextMonth"
        >
          &rsaquo;
        </button>
      </div>

      <div class="grid grid-cols-7 gap-1 text-center text-xs font-medium text-slate-500">
        <span v-for="label in WEEKDAY_LABELS" :key="label">{{ label }}</span>
      </div>

      <div class="mt-1 grid grid-cols-7 gap-1">
        <button
          v-for="day in days"
          :key="day.dateKey"
          type="button"
          :disabled="!isSelectable(day)"
          :aria-label="dayAriaLabel(day)"
          :aria-pressed="modelValue === day.dateKey"
          class="flex h-14 flex-col items-center justify-center rounded-md text-sm transition"
          :class="dayClasses(day)"
          @click="selectDay(day)"
        >
          <span>{{ day.dayNumber }}</span>
          <span
            v-if="day.slotCount > 0"
            class="text-[10px]"
            :class="modelValue === day.dateKey ? 'text-sky-100' : 'text-sky-600'"
          >
            {{ day.slotCount }} slot{{ day.slotCount === 1 ? "" : "s" }}
          </span>
        </button>
      </div>
    </div>

    <div class="rounded-lg border border-slate-200 bg-white p-4">
      <h3 class="text-sm font-semibold text-slate-700">Available times</h3>

      <p v-if="availableSlots.length === 0" class="mt-2 text-sm text-slate-500">
        This calendar has no available times right now.
      </p>
      <p v-else-if="!modelValue" class="mt-2 text-sm text-slate-500">
        Select a date to see available times.
      </p>
      <p v-else-if="selectedDateSlots.length === 0" class="mt-2 text-sm text-slate-500">
        No available slots on this date.
      </p>
      <ul v-else class="mt-2 divide-y divide-slate-200">
        <li v-for="slot in selectedDateSlots" :key="slot.start" class="flex items-center justify-between py-2">
          <span class="text-sm text-slate-800">{{ formatSlotRange(slot) }}</span>
          <button
            type="button"
            :disabled="actionPendingId === slot.start"
            class="text-sm font-semibold text-sky-600 hover:text-sky-500 disabled:cursor-not-allowed disabled:opacity-50"
            @click="emit('slotAction', slot)"
          >
            {{ actionPendingId === slot.start ? "Working…" : actionLabel }}
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>
