<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";

import { ApiError } from "../api/client";
import type { Booking, EventType, Slot } from "../api/types";
import CalendarPicker from "../shared/CalendarPicker.vue";
import { dateKeyFromIso, formatBookingDateTime, formatSlotRange } from "../shared/dateTime";
import { createBooking, listEventTypes, listSlots } from "./api";

const BOOKING_ERROR_COPY: Record<string, string> = {
  slot_occupied: "This slot was just taken. Please choose another time.",
  slot_outside_window: "This time is no longer available. Please select a different slot.",
  slot_mismatch: "Invalid time selected. Please choose from the available slots.",
};

const route = useRoute();
const eventTypeId = computed(() => String(route.params.eventTypeId ?? ""));

const loading = ref(true);
const notFound = ref(false);
const errorMessage = ref<string | null>(null);
const eventType = ref<EventType | null>(null);
const availableSlots = ref<Slot[]>([]);
const selectedDate = ref<string | null>(null);
const pendingSlot = ref<Slot | null>(null);
const guestName = ref("");
const submitting = ref(false);
const confirmation = ref<Booking | null>(null);
const actionPendingId = ref<string | null>(null);

async function loadPage(): Promise<void> {
  loading.value = true;
  errorMessage.value = null;
  notFound.value = false;
  try {
    const catalog = await listEventTypes();
    const match = catalog.eventTypes.find((item) => item.id === eventTypeId.value);
    if (!match) {
      notFound.value = true;
      return;
    }
    eventType.value = match;
    const slots = await listSlots(eventTypeId.value);
    availableSlots.value = slots.availableSlots;
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "Could not load this event type.";
  } finally {
    loading.value = false;
  }
}

async function refreshSlots(): Promise<void> {
  const slots = await listSlots(eventTypeId.value);
  availableSlots.value = slots.availableSlots;
}

function openConfirm(slot: Slot): void {
  pendingSlot.value = slot;
  guestName.value = "";
  errorMessage.value = null;
}

function closeConfirm(): void {
  if (submitting.value) {
    return;
  }
  pendingSlot.value = null;
  guestName.value = "";
}

async function confirmBooking(): Promise<void> {
  if (!pendingSlot.value || !eventType.value) {
    return;
  }
  const name = guestName.value.trim();
  if (!name) {
    errorMessage.value = "Please enter your name to confirm this booking.";
    return;
  }

  submitting.value = true;
  actionPendingId.value = pendingSlot.value.start;
  errorMessage.value = null;
  try {
    confirmation.value = await createBooking({
      eventTypeId: eventType.value.id,
      slotStart: pendingSlot.value.start,
      guestName: name,
    });
    pendingSlot.value = null;
    guestName.value = "";
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = BOOKING_ERROR_COPY[error.code] ?? error.message;
      if (error.code === "slot_occupied") {
        await refreshSlots();
      }
    } else {
      errorMessage.value = "Could not complete the booking. Please try again.";
    }
  } finally {
    submitting.value = false;
    actionPendingId.value = null;
  }
}

onMounted(loadPage);
</script>

<template>
  <section>
    <p v-if="loading" class="text-slate-500">Loading calendar…</p>

    <div v-else-if="notFound">
      <h1 class="text-2xl font-semibold">Event type not found</h1>
      <p class="mt-2 text-slate-600">This event type is not in the public catalog.</p>
      <RouterLink to="/" class="mt-4 inline-block font-medium text-sky-700">Back to event types</RouterLink>
    </div>

    <div v-else-if="eventType && confirmation" class="rounded-lg border border-emerald-200 bg-emerald-50 p-6">
      <h1 class="text-2xl font-semibold text-emerald-900">Booking confirmed</h1>
      <p class="mt-2 text-emerald-900">
        {{ confirmation.eventTypeTitle }} with {{ confirmation.guestName }} at
        {{ formatBookingDateTime(confirmation.start) }}.
      </p>
      <RouterLink to="/" class="mt-4 inline-block font-medium text-sky-700">Book another call</RouterLink>
    </div>

    <div v-else-if="eventType">
      <h1 class="text-2xl font-semibold">{{ eventType.title }}</h1>
      <p class="mt-1 text-slate-600">{{ eventType.description }}</p>
      <p class="mt-1 text-sm font-medium text-slate-700">{{ eventType.durationMinutes }} min</p>

      <p v-if="errorMessage && !pendingSlot" role="alert" class="mt-4 text-red-700">{{ errorMessage }}</p>

      <div class="mt-6">
        <CalendarPicker
          v-model="selectedDate"
          :available-slots="availableSlots"
          :action-pending-id="actionPendingId"
          @book="openConfirm"
        />
      </div>
    </div>

    <div
      v-if="pendingSlot && eventType"
      class="fixed inset-0 z-10 flex items-center justify-center bg-slate-900/40 p-4"
    >
      <form
        class="w-full max-w-md rounded-lg bg-white p-6 shadow-lg"
        @submit.prevent="confirmBooking"
      >
        <h2 class="text-lg font-semibold">Confirm booking</h2>
        <p class="mt-2 text-sm text-slate-600">
          {{ eventType.title }} · {{ formatSlotRange(pendingSlot) }}
          ({{ dateKeyFromIso(pendingSlot.start) }})
        </p>
        <p v-if="errorMessage" role="alert" class="mt-3 text-sm text-red-700">{{ errorMessage }}</p>
        <label class="mt-4 block text-sm font-medium" for="guest-name">Your name</label>
        <input
          id="guest-name"
          v-model="guestName"
          type="text"
          name="guestName"
          autocomplete="name"
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
          required
        />
        <div class="mt-4 flex justify-end gap-3">
          <button type="button" class="text-sm text-slate-600" :disabled="submitting" @click="closeConfirm">
            Cancel
          </button>
          <button
            type="submit"
            class="rounded-md bg-sky-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
            :disabled="submitting"
          >
            Confirm booking
          </button>
        </div>
      </form>
    </div>
  </section>
</template>
