<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, type OwnerCalendar, type Slot } from '../shared/apiClient'
import SlotDayList from '../shared/SlotDayList.vue'

const props = defineProps<{ ownerId: string }>()
const calendar = ref<OwnerCalendar>()
const error = ref('')
const selectedDay = ref(new Date().toISOString().slice(0, 10))
const startTime = ref('')
const endTime = ref('')
const timeOptions = Array.from({ length: 48 }, (_, index) => {
  const hours = Math.floor(index / 2).toString().padStart(2, '0')
  const minutes = index % 2 === 0 ? '00' : '30'
  return `${hours}:${minutes}`
})
async function load(): Promise<void> { try { calendar.value = await api<OwnerCalendar>(`/calendars/${props.ownerId}/owner`) } catch (reason) { error.value = reason instanceof Error ? reason.message : 'Could not load calendar.' } }
async function add(): Promise<void> {
  try {
    await api(`/calendars/${props.ownerId}/availability`, {
      method: 'POST',
      body: JSON.stringify({
        start: `${selectedDay.value}T${startTime.value}:00Z`,
        end: `${selectedDay.value}T${endTime.value}:00Z`,
      }),
    })
    startTime.value = ''
    endTime.value = ''
    await load()
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : 'Could not add availability.'
  }
}
async function remove(slot: Slot): Promise<void> { await api(`/calendars/${props.ownerId}/availability/${encodeURIComponent(slot.start)}`, { method: 'DELETE' }); await load() }
async function cancel(id: string): Promise<void> { await api(`/calendars/${props.ownerId}/owner/bookings/${id}`, { method: 'DELETE' }); await load() }
function displayBookingDate(value: string): string { return `${value.slice(0, 4)}.${value.slice(5, 7)}.${value.slice(8, 10)} ${value.slice(11, 16)}` }
onMounted(load)
</script>
<template>
  <section class="space-y-6"><h1 class="text-2xl font-bold">Calendar: {{ ownerId }}</h1><p>Share <code>/cal/{{ ownerId }}</code></p>
    <p v-if="error" class="text-red-700">{{ error }}</p><h2 class="text-xl font-semibold">Availability</h2>
    <SlotDayList v-if="calendar" :slots="calendar.availableSlots" action-label="Remove" allow-empty-day-selection @action="remove" @select-day="selectedDay = $event" />
    <form class="flex flex-wrap items-end gap-2 rounded-xl border border-slate-200 bg-white p-4" @submit.prevent="add">
      <p class="w-full text-sm text-slate-600">Add a time frame for <strong>{{ selectedDay }}</strong> (UTC).</p>
      <label class="grid gap-1 text-sm font-medium">Start time
        <select v-model="startTime" required>
          <option disabled value="">Choose a start time</option>
          <option v-for="time in timeOptions" :key="time" :value="time">{{ time }}</option>
        </select>
      </label>
      <label class="grid gap-1 text-sm font-medium">End time
        <select v-model="endTime" required>
          <option disabled value="">Choose an end time</option>
          <option v-for="time in timeOptions" :key="time" :value="time">{{ time }}</option>
        </select>
      </label>
      <button>Publish availability</button>
    </form>
    <h2 class="text-xl font-semibold">Booked meetings</h2><div v-if="calendar?.bookings.length" class="space-y-2"><div v-for="booking in calendar.bookings" :key="booking.id" class="flex justify-between rounded bg-white p-3">{{ displayBookingDate(booking.start) }} · {{ booking.visitorName }}<button @click="cancel(booking.id)">Cancel</button></div></div><p v-else>No upcoming bookings.</p>
  </section>
</template>
