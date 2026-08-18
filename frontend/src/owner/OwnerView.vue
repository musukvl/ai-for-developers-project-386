<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, type OwnerCalendar, type Slot } from '../shared/apiClient'
import SlotDayList from '../shared/SlotDayList.vue'

const props = defineProps<{ ownerId: string }>()
const calendar = ref<OwnerCalendar>()
const error = ref('')
const start = ref('')
const end = ref('')
async function load(): Promise<void> { try { calendar.value = await api<OwnerCalendar>(`/calendars/${props.ownerId}/owner`) } catch (reason) { error.value = reason instanceof Error ? reason.message : 'Could not load calendar.' } }
async function add(): Promise<void> { try { await api(`/calendars/${props.ownerId}/availability`, { method: 'POST', body: JSON.stringify({ start: new Date(start.value).toISOString(), end: new Date(end.value).toISOString() }) }); start.value = ''; end.value = ''; await load() } catch (reason) { error.value = reason instanceof Error ? reason.message : 'Could not add availability.' } }
async function remove(slot: Slot): Promise<void> { await api(`/calendars/${props.ownerId}/availability/${encodeURIComponent(slot.start)}`, { method: 'DELETE' }); await load() }
async function cancel(id: string): Promise<void> { await api(`/calendars/${props.ownerId}/owner/bookings/${id}`, { method: 'DELETE' }); await load() }
onMounted(load)
</script>
<template>
  <section class="space-y-6"><h1 class="text-2xl font-bold">Calendar: {{ ownerId }}</h1><p>Share <code>/cal/{{ ownerId }}</code></p>
    <form class="flex flex-wrap gap-2" @submit.prevent="add"><input v-model="start" type="datetime-local" required /><input v-model="end" type="datetime-local" required /><button>Publish availability</button></form>
    <p v-if="error" class="text-red-700">{{ error }}</p><h2 class="text-xl font-semibold">Available times</h2><SlotDayList v-if="calendar" :slots="calendar.availableSlots" action-label="Remove" @action="remove" />
    <h2 class="text-xl font-semibold">Booked meetings</h2><div v-if="calendar?.bookings.length" class="space-y-2"><div v-for="booking in calendar.bookings" :key="booking.id" class="flex justify-between rounded bg-white p-3">{{ booking.start }} · {{ booking.visitorName }}<button @click="cancel(booking.id)">Cancel</button></div></div><p v-else>No upcoming bookings.</p>
  </section>
</template>
