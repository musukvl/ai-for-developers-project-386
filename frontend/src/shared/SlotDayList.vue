<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Slot } from './apiClient'

const props = withDefaults(defineProps<{ slots: Slot[]; actionLabel: string; allowEmptyDaySelection?: boolean }>(), {
  allowEmptyDaySelection: false,
})
const emit = defineEmits<{ action: [slot: Slot]; selectDay: [date: string] }>()

const selectedDate = ref('')
const displayedMonth = ref(new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), 1)))
const today = new Date().toISOString().slice(0, 10)

const slotsByDate = computed(() =>
  props.slots.reduce<Record<string, Slot[]>>((groupedSlots, slot) => {
    const dateKey = slot.start.slice(0, 10)
    ;(groupedSlots[dateKey] ??= []).push(slot)
    return groupedSlots
  }, {}),
)

const selectedSlots = computed(() => slotsByDate.value[selectedDate.value] ?? [])
const monthLabel = computed(() =>
  new Intl.DateTimeFormat('en', { month: 'long', year: 'numeric', timeZone: 'UTC' }).format(displayedMonth.value),
)

const calendarDays = computed(() => {
  const year = displayedMonth.value.getUTCFullYear()
  const month = displayedMonth.value.getUTCMonth()
  const firstDay = new Date(Date.UTC(year, month, 1))
  const gridStart = new Date(firstDay)
  gridStart.setUTCDate(1 - ((firstDay.getUTCDay() + 6) % 7))
  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(gridStart)
    date.setUTCDate(gridStart.getUTCDate() + index)
    const key = date.toISOString().slice(0, 10)
    return {
      key,
      day: date.getUTCDate(),
      isCurrentMonth: date.getUTCMonth() === month,
      isPast: key < today,
      slotCount: slotsByDate.value[key]?.length ?? 0,
    }
  })
})

watch(
  () => props.slots,
  (slots) => {
    if (!slots.length) {
      if (props.allowEmptyDaySelection && !selectedDate.value) {
        selectedDate.value = new Date().toISOString().slice(0, 10)
      } else if (!props.allowEmptyDaySelection) {
        selectedDate.value = ''
      }
      return
    }
    if (!slotsByDate.value[selectedDate.value]) {
      selectedDate.value = slots[0].start.slice(0, 10)
      displayedMonth.value = new Date(`${selectedDate.value}T00:00:00Z`)
    }
  },
  { immediate: true },
)

function previousMonth(): void {
  displayedMonth.value = new Date(Date.UTC(displayedMonth.value.getUTCFullYear(), displayedMonth.value.getUTCMonth() - 1, 1))
}

function nextMonth(): void {
  displayedMonth.value = new Date(Date.UTC(displayedMonth.value.getUTCFullYear(), displayedMonth.value.getUTCMonth() + 1, 1))
}

function selectDay(date: string): void {
  selectedDate.value = date
  emit('selectDay', date)
}

function displaySelectedDate(value: string): string {
  return new Intl.DateTimeFormat('en', { dateStyle: 'full', timeZone: 'UTC' }).format(new Date(`${value}T00:00:00Z`))
}

function displayTime(value: string): string {
  return new Intl.DateTimeFormat('en', {
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
    timeZone: 'UTC',
  }).format(new Date(value))
}
</script>

<template>
  <div v-if="slots.length || allowEmptyDaySelection" class="grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(18rem,0.75fr)]">
    <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="mb-5 flex items-center justify-between">
        <h3 class="text-lg font-semibold">Calendar</h3>
        <div class="flex gap-2">
          <button class="calendar-nav" aria-label="Previous month" @click="previousMonth">←</button>
          <button class="calendar-nav" aria-label="Next month" @click="nextMonth">→</button>
        </div>
      </div>
      <p class="mb-4 font-medium">{{ monthLabel }}</p>
      <div class="grid grid-cols-7 gap-1 text-center text-xs font-semibold text-slate-500">
        <span v-for="day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="day">{{ day }}</span>
      </div>
      <div class="mt-2 grid grid-cols-7 gap-1">
        <button
          v-for="day in calendarDays"
          :key="day.key"
          class="calendar-day"
          :class="{ 'calendar-day--outside': !day.isCurrentMonth, 'calendar-day--past': day.isPast, 'calendar-day--available': day.slotCount && !day.isPast, 'calendar-day--selected': selectedDate === day.key }"
          :disabled="day.isPast || (!day.slotCount && !allowEmptyDaySelection)"
          :aria-label="`${day.key}${day.slotCount ? `, ${day.slotCount} available slots` : ''}`"
          @click="selectDay(day.key)"
        >
          <span>{{ day.day }}</span><small v-if="day.slotCount">{{ day.slotCount }} slots</small>
        </button>
      </div>
    </section>

    <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 class="text-lg font-semibold">Available times</h3>
      <p class="mb-4 text-sm text-slate-600">{{ displaySelectedDate(selectedDate) }}</p>
      <div class="space-y-2">
        <button v-for="slot in selectedSlots" :key="slot.start" class="slot-action" @click="emit('action', slot)">
          <span>{{ displayTime(slot.start) }}–{{ displayTime(slot.end) }}</span><strong>{{ actionLabel }}</strong>
        </button>
      </div>
      <p v-if="!selectedSlots.length" class="rounded bg-slate-50 p-3 text-sm text-slate-600">No available slots on this day.</p>
    </section>
  </div>
  <p v-else class="rounded bg-white p-4 text-slate-600">No available slots.</p>
</template>
