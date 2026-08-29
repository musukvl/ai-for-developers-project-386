<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { ApiError } from "../api/client";
import type { Booking, EventType } from "../api/types";
import { formatBookingDateTime } from "../shared/dateTime";
import { cancelBooking, deleteEventType, listEventTypes, listOwnerBookings } from "./api";
import CreateEventTypeForm from "./CreateEventTypeForm.vue";

const loading = ref(true);
const errorMessage = ref<string | null>(null);
const eventTypes = ref<EventType[]>([]);
const bookings = ref<Booking[]>([]);
const pendingDeleteId = ref<string | null>(null);

const publicUrl = `${window.location.origin}/`;

async function load(): Promise<void> {
  loading.value = true;
  errorMessage.value = null;
  try {
    const [catalog, upcoming] = await Promise.all([listEventTypes(), listOwnerBookings()]);
    eventTypes.value = catalog.eventTypes;
    bookings.value = upcoming.bookings;
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "Could not load owner data.";
  } finally {
    loading.value = false;
  }
}

async function confirmDelete(eventTypeId: string): Promise<void> {
  errorMessage.value = null;
  try {
    await deleteEventType(eventTypeId);
    pendingDeleteId.value = null;
    await load();
  } catch (error) {
    if (error instanceof ApiError && error.code === "future_bookings_exist") {
      errorMessage.value = "Cannot delete — cancel all upcoming bookings for this event type first.";
    } else {
      errorMessage.value = error instanceof ApiError ? error.message : "Could not delete event type.";
    }
  }
}

async function onCancelBooking(bookingId: string): Promise<void> {
  errorMessage.value = null;
  try {
    await cancelBooking(bookingId);
    await load();
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "Could not cancel booking.";
  }
}

onMounted(load);
</script>

<template>
  <section class="space-y-8">
    <header>
      <h1 class="text-2xl font-semibold">Owner</h1>
      <p class="mt-1 text-slate-600">Manage event types and upcoming meetings. No sign-in required.</p>
      <p class="mt-2 text-sm">
        Public calendar:
        <RouterLink to="/" class="font-medium text-sky-700">{{ publicUrl }}</RouterLink>
      </p>
    </header>

    <p v-if="errorMessage" role="alert" class="text-red-700">{{ errorMessage }}</p>
    <p v-if="loading" class="text-slate-500">Loading owner data…</p>

    <CreateEventTypeForm @created="load" />

    <section>
      <h2 class="text-lg font-semibold">Event types</h2>
      <p v-if="!loading && eventTypes.length === 0" class="mt-2 text-slate-500">
        No event types yet. Create one above.
      </p>
      <ul v-else class="mt-3 space-y-3">
        <li
          v-for="eventType in eventTypes"
          :key="eventType.id"
          class="rounded-lg border border-slate-200 bg-white p-4"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h3 class="font-semibold">{{ eventType.title }}</h3>
              <p class="text-sm text-slate-600">{{ eventType.description }}</p>
              <p class="mt-1 text-sm">{{ eventType.durationMinutes }} min</p>
            </div>
            <button
              v-if="pendingDeleteId !== eventType.id"
              type="button"
              class="text-sm font-semibold text-red-700"
              @click="pendingDeleteId = eventType.id"
            >
              Delete
            </button>
            <div v-else class="flex gap-2 text-sm">
              <span>Delete this event type?</span>
              <button type="button" class="font-semibold text-red-700" @click="confirmDelete(eventType.id)">
                Confirm
              </button>
              <button type="button" class="text-slate-600" @click="pendingDeleteId = null">Keep</button>
            </div>
          </div>
        </li>
      </ul>
    </section>

    <section>
      <h2 class="text-lg font-semibold">Booked meetings</h2>
      <p v-if="!loading && bookings.length === 0" class="mt-2 text-slate-500">No upcoming meetings.</p>
      <ul v-else class="mt-3 space-y-3">
        <li
          v-for="booking in bookings"
          :key="booking.id"
          class="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-4"
        >
          <div>
            <p class="font-medium">{{ formatBookingDateTime(booking.start) }}</p>
            <p class="text-sm text-slate-600">{{ booking.eventTypeTitle }} · {{ booking.guestName }}</p>
          </div>
          <button
            type="button"
            class="text-sm font-semibold text-red-700"
            @click="onCancelBooking(booking.id)"
          >
            Cancel
          </button>
        </li>
      </ul>
    </section>
  </section>
</template>
