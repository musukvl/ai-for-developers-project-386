<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, ApiError, type Slot, type VisitorCalendar } from '../shared/apiClient'
import SlotDayList from '../shared/SlotDayList.vue'
import CalendarNotFound from './CalendarNotFound.vue'
const props = defineProps<{ ownerId: string }>()
const calendar = ref<VisitorCalendar>()
const error = ref('')
const notFound = ref(false)
async function load(): Promise<void> { try { calendar.value = await api<VisitorCalendar>(`/calendars/${props.ownerId}`) } catch (reason) { notFound.value = reason instanceof ApiError && reason.code === 'not_found'; error.value = reason instanceof Error ? reason.message : 'Could not load calendar.' } }
async function book(slot: Slot): Promise<void> { try { await api(`/calendars/${props.ownerId}/bookings`, { method: 'POST', body: JSON.stringify({ slotStart: slot.start }) }); await load() } catch (reason) { if (reason instanceof ApiError && reason.code === 'conflict') { await load(); error.value = 'That slot was just taken. The calendar was refreshed.' } else error.value = reason instanceof Error ? reason.message : 'Could not book slot.' } }
async function cancel(id: string): Promise<void> { await api(`/calendars/${props.ownerId}/bookings/${id}`, { method: 'DELETE' }); await load() }
function displayBookingDate(value: string): string { return `${value.slice(0, 4)}.${value.slice(5, 7)}.${value.slice(8, 10)} ${value.slice(11, 16)}` }
onMounted(load)
</script>
<template><CalendarNotFound v-if="notFound" /><section v-else class="space-y-5"><h1 class="text-2xl font-bold">{{ ownerId }}'s calendar</h1><p v-if="error" class="text-red-700">{{ error }}</p><h2 class="text-xl font-semibold">Available times</h2><SlotDayList v-if="calendar" :slots="calendar.availableSlots" action-label="Book" @action="book" /><h2 class="text-xl font-semibold">My bookings</h2><div v-if="calendar?.myBookings.length" class="space-y-2"><div v-for="booking in calendar.myBookings" :key="booking.id" class="flex justify-between rounded bg-white p-3">{{ displayBookingDate(booking.start) }}<button @click="cancel(booking.id)">Cancel</button></div></div><p v-else>No bookings yet.</p></section></template>
