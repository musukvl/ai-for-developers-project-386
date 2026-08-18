<script setup lang="ts">
import type { Slot } from './apiClient'

defineProps<{ slots: Slot[]; actionLabel: string }>()
const emit = defineEmits<{ action: [slot: Slot] }>()

function displayDay(value: string): string {
  return new Intl.DateTimeFormat('en', { dateStyle: 'full', timeZone: 'UTC' }).format(new Date(value))
}
function displayTime(value: string): string {
  return new Intl.DateTimeFormat('en', { timeStyle: 'short', timeZone: 'UTC' }).format(new Date(value))
}
</script>

<template>
  <div v-if="slots.length" class="space-y-3">
    <section v-for="slot in slots" :key="slot.start" class="flex items-center justify-between rounded border bg-white p-3">
      <span><span class="font-medium">{{ displayDay(slot.start) }}</span> · {{ displayTime(slot.start) }}–{{ displayTime(slot.end) }} UTC</span>
      <button @click="emit('action', slot)">{{ actionLabel }}</button>
    </section>
  </div>
  <p v-else class="rounded bg-white p-4 text-slate-600">No available slots.</p>
</template>
