<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import type { OwnerCalendar, Slot } from "../api/types";
import { ApiError } from "../api/client";
import CalendarPicker from "../shared/CalendarPicker.vue";
import { formatBookingDateTime } from "../shared/dateTime";
import CreateCalendarForm from "./CreateCalendarForm.vue";
import { addAvailability, cancelBookingAsOwner, getOwnerCalendar, removeAvailabilitySlot } from "./api";

const props = defineProps<{ ownerId: string }>();

const calendar = ref<OwnerCalendar | null>(null);
const loading = ref(true);
const notFound = ref(false);
const loadErrorMessage = ref("");

const selectedDate = ref<string | null>(null);
const pendingSlotStart = ref<string | null>(null);
const slotActionError = ref("");

const startTime = ref("09:00");
const endTime = ref("09:30");
const isPublishing = ref(false);
const availabilityError = ref("");

const timeOptions = (() => {
  const options: string[] = [];
  for (let hour = 0; hour < 24; hour += 1) {
    for (const minute of [0, 30]) {
      options.push(`${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`);
    }
  }
  return options;
})();

const canPublish = computed(
  () => Boolean(selectedDate.value) && endTime.value > startTime.value && !isPublishing.value
);

async function loadCalendar(): Promise<void> {
  loading.value = true;
  loadErrorMessage.value = "";
  notFound.value = false;
  try {
    calendar.value = await getOwnerCalendar(props.ownerId);
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

async function handlePublishAvailability(): Promise<void> {
  if (!selectedDate.value) {
    return;
  }
  availabilityError.value = "";
  if (endTime.value <= startTime.value) {
    availabilityError.value = "End time must be after start time.";
    return;
  }

  isPublishing.value = true;
  try {
    const start = `${selectedDate.value}T${startTime.value}:00Z`;
    const end = `${selectedDate.value}T${endTime.value}:00Z`;
    const result = await addAvailability(props.ownerId, start, end);
    if (calendar.value) {
      calendar.value = { ...calendar.value, availableSlots: result.availableSlots };
    }
  } catch (error) {
    availabilityError.value =
      error instanceof ApiError ? error.message : "Could not publish availability.";
  } finally {
    isPublishing.value = false;
  }
}

async function handleRemoveSlot(slot: Slot): Promise<void> {
  slotActionError.value = "";
  pendingSlotStart.value = slot.start;
  try {
    await removeAvailabilitySlot(props.ownerId, slot.start);
    await loadCalendar();
  } catch (error) {
    slotActionError.value =
      error instanceof ApiError ? error.message : "Could not remove the slot.";
  } finally {
    pendingSlotStart.value = null;
  }
}

const pendingBookingId = ref<string | null>(null);
const bookingActionError = ref("");

async function handleCancelBooking(bookingId: string): Promise<void> {
  bookingActionError.value = "";
  pendingBookingId.value = bookingId;
  try {
    await cancelBookingAsOwner(props.ownerId, bookingId);
    await loadCalendar();
  } catch (error) {
    bookingActionError.value =
      error instanceof ApiError ? error.message : "Could not cancel the booking.";
  } finally {
    pendingBookingId.value = null;
  }
}
</script>

<template>
  <div v-if="loading" class="text-sm text-slate-500">Loading calendar…</div>
  <CreateCalendarForm v-else-if="notFound" :owner-id="ownerId" />
  <p v-else-if="loadErrorMessage" role="alert" class="text-sm text-red-600">{{ loadErrorMessage }}</p>
  <div v-else-if="calendar" class="space-y-6">
    <section>
      <h2 class="text-xl font-semibold text-slate-900">{{ ownerId }}'s calendar</h2>
      <p class="text-sm text-slate-600">
        Share this calendar:
        <code class="rounded bg-slate-100 px-1">/cal/{{ ownerId }}</code>
      </p>
    </section>

    <p v-if="slotActionError" role="alert" class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
      {{ slotActionError }}
    </p>

    <CalendarPicker
      v-model="selectedDate"
      mode="owner"
      :available-slots="calendar.availableSlots"
      action-label="Remove"
      :action-pending-id="pendingSlotStart"
      @slot-action="handleRemoveSlot"
    />

    <section class="rounded-lg border border-slate-200 bg-white p-4">
      <h3 class="text-lg font-semibold text-slate-800">Add a time frame</h3>
      <p v-if="!selectedDate" class="mt-2 text-sm text-slate-500">
        Select a date above to add availability.
      </p>
      <form v-else class="mt-3 flex flex-wrap items-end gap-3" @submit.prevent="handlePublishAvailability">
        <div>
          <label class="block text-sm font-medium text-slate-700" for="start-time">Start time</label>
          <select
            id="start-time"
            v-model="startTime"
            class="mt-1 rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          >
            <option v-for="time in timeOptions" :key="time" :value="time">{{ time }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700" for="end-time">End time</label>
          <select
            id="end-time"
            v-model="endTime"
            class="mt-1 rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          >
            <option v-for="time in timeOptions" :key="time" :value="time">{{ time }}</option>
          </select>
        </div>
        <button
          type="submit"
          :disabled="!canPublish"
          class="rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {{ isPublishing ? "Publishing…" : "Publish availability" }}
        </button>
      </form>
      <p v-if="availabilityError" role="alert" class="mt-2 text-sm text-red-600">
        {{ availabilityError }}
      </p>
    </section>

    <section>
      <h3 class="text-lg font-semibold text-slate-800">Booked meetings</h3>
      <p v-if="bookingActionError" role="alert" class="mt-2 text-sm text-red-600">
        {{ bookingActionError }}
      </p>
      <p v-if="calendar.bookings.length === 0" class="mt-2 text-sm text-slate-500">
        No upcoming bookings yet.
      </p>
      <ul v-else class="mt-2 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
        <li
          v-for="booking in calendar.bookings"
          :key="booking.id"
          class="flex items-center justify-between px-4 py-3"
        >
          <div>
            <p class="text-sm font-medium text-slate-800">{{ formatBookingDateTime(booking.start) }}</p>
            <p class="text-sm text-slate-500">{{ booking.visitorName }}</p>
          </div>
          <button
            type="button"
            :disabled="pendingBookingId === booking.id"
            class="text-sm font-semibold text-red-600 hover:text-red-500 disabled:cursor-not-allowed disabled:opacity-50"
            @click="handleCancelBooking(booking.id)"
          >
            {{ pendingBookingId === booking.id ? "Cancelling…" : "Cancel" }}
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>
