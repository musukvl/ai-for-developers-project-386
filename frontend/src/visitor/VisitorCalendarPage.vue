<script setup lang="ts">
import { onMounted, ref } from "vue";

import type { Slot, VisitorCalendar } from "../api/types";
import { ApiError } from "../api/client";
import CalendarPicker from "../shared/CalendarPicker.vue";
import { formatBookingDateTime } from "../shared/dateTime";
import CalendarNotFound from "./CalendarNotFound.vue";
import { cancelBookingAsVisitor, createBooking, getVisitorCalendar } from "./api";

const props = defineProps<{ ownerId: string }>();

const calendar = ref<VisitorCalendar | null>(null);
const loading = ref(true);
const notFound = ref(false);
const loadErrorMessage = ref("");

const selectedDate = ref<string | null>(null);
const pendingSlotStart = ref<string | null>(null);
const bookingErrorMessage = ref("");
const staleViewMessage = ref("");

const pendingBookingId = ref<string | null>(null);
const cancelErrorMessage = ref("");

async function loadCalendar(): Promise<void> {
  loading.value = true;
  loadErrorMessage.value = "";
  notFound.value = false;
  try {
    calendar.value = await getVisitorCalendar(props.ownerId);
  } catch (error) {
    if (error instanceof ApiError && error.code === "not_found") {
      notFound.value = true;
    } else {
      loadErrorMessage.value =
        error instanceof ApiError ? error.message : "Failed to load the calendar.";
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadCalendar);

async function handleBook(slot: Slot): Promise<void> {
  bookingErrorMessage.value = "";
  staleViewMessage.value = "";
  pendingSlotStart.value = slot.start;
  try {
    await createBooking(props.ownerId, slot.start);
    await loadCalendar();
  } catch (error) {
    if (error instanceof ApiError && error.code === "conflict") {
      staleViewMessage.value = "That slot was just taken. Here are the current available times.";
      await loadCalendar();
    } else {
      bookingErrorMessage.value =
        error instanceof ApiError ? error.message : "Could not book the slot.";
    }
  } finally {
    pendingSlotStart.value = null;
  }
}

async function handleCancel(bookingId: string): Promise<void> {
  cancelErrorMessage.value = "";
  pendingBookingId.value = bookingId;
  try {
    await cancelBookingAsVisitor(props.ownerId, bookingId);
    await loadCalendar();
  } catch (error) {
    cancelErrorMessage.value =
      error instanceof ApiError ? error.message : "Could not cancel the booking.";
  } finally {
    pendingBookingId.value = null;
  }
}
</script>

<template>
  <div v-if="loading" class="text-sm text-slate-500">Loading calendar…</div>
  <CalendarNotFound v-else-if="notFound" />
  <p v-else-if="loadErrorMessage" role="alert" class="text-sm text-red-600">{{ loadErrorMessage }}</p>
  <div v-else-if="calendar" class="space-y-6">
    <section>
      <h2 class="text-xl font-semibold text-slate-900">{{ ownerId }}'s calendar</h2>
      <p class="text-sm text-slate-600">Book a 30-minute meeting with {{ ownerId }}.</p>
    </section>

    <p v-if="staleViewMessage" role="status" class="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
      {{ staleViewMessage }}
    </p>
    <p v-if="bookingErrorMessage" role="alert" class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
      {{ bookingErrorMessage }}
    </p>

    <CalendarPicker
      v-model="selectedDate"
      mode="visitor"
      :available-slots="calendar.availableSlots"
      action-label="Book"
      :action-pending-id="pendingSlotStart"
      @slot-action="handleBook"
    />

    <section>
      <h3 class="text-lg font-semibold text-slate-800">My bookings</h3>
      <p v-if="cancelErrorMessage" role="alert" class="mt-2 text-sm text-red-600">
        {{ cancelErrorMessage }}
      </p>
      <p v-if="calendar.myBookings.length === 0" class="mt-2 text-sm text-slate-500">
        You have no upcoming bookings.
      </p>
      <ul v-else class="mt-2 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
        <li
          v-for="booking in calendar.myBookings"
          :key="booking.id"
          class="flex items-center justify-between px-4 py-3"
        >
          <span class="text-sm font-medium text-slate-800">{{ formatBookingDateTime(booking.start) }}</span>
          <button
            type="button"
            :disabled="pendingBookingId === booking.id"
            class="text-sm font-semibold text-red-600 hover:text-red-500 disabled:cursor-not-allowed disabled:opacity-50"
            @click="handleCancel(booking.id)"
          >
            {{ pendingBookingId === booking.id ? "Cancelling…" : "Cancel" }}
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>
