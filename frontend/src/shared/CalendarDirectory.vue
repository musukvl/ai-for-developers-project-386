<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import type { CalendarDirectoryEntry } from "../api/types";
import { ApiError } from "../api/client";
import { getCalendarDirectory } from "./calendarDirectoryApi";

const props = defineProps<{ currentOwnerId: string }>();

const calendars = ref<CalendarDirectoryEntry[]>([]);
const loading = ref(true);
const errorMessage = ref("");

const otherCalendars = computed(() =>
  calendars.value
    .filter((calendar) => calendar.ownerId !== props.currentOwnerId)
    .sort((left, right) => left.ownerId.localeCompare(right.ownerId))
);

async function loadDirectory(): Promise<void> {
  loading.value = true;
  errorMessage.value = "";
  try {
    const directory = await getCalendarDirectory();
    calendars.value = directory.calendars;
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : "Failed to load other calendars.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadDirectory);
</script>

<template>
  <section class="rounded-lg border border-slate-200 bg-white p-4" aria-labelledby="other-calendars-title">
    <h2 id="other-calendars-title" class="text-lg font-semibold text-slate-800">Other calendars</h2>
    <p v-if="loading" class="mt-2 text-sm text-slate-500">Loading other calendars…</p>
    <p v-else-if="errorMessage" role="alert" class="mt-2 text-sm text-red-600">
      {{ errorMessage }}
    </p>
    <p v-else-if="otherCalendars.length === 0" class="mt-2 text-sm text-slate-500">
      No other calendars are available.
    </p>
    <ul v-else class="mt-2 space-y-1">
      <li v-for="calendar in otherCalendars" :key="calendar.ownerId">
        <RouterLink
          :to="`/cal/${encodeURIComponent(calendar.ownerId)}`"
          class="text-sm font-medium text-sky-700 underline hover:text-sky-600"
        >
          {{ calendar.ownerId }}
        </RouterLink>
      </li>
    </ul>
  </section>
</template>
