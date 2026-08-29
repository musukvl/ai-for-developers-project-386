<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import { ApiError } from "../api/client";
import type { EventType } from "../api/types";
import { listEventTypes } from "./api";

const eventTypes = ref<EventType[]>([]);
const loading = ref(true);
const errorMessage = ref<string | null>(null);

onMounted(async () => {
  try {
    const response = await listEventTypes();
    eventTypes.value = response.eventTypes;
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : "Could not load event types.";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <section>
    <h1 class="text-2xl font-semibold">Book a call</h1>
    <p class="mt-1 text-slate-600">Choose an event type. No account is required.</p>

    <p v-if="loading" class="mt-6 text-slate-500">Loading event types…</p>
    <p v-else-if="errorMessage" role="alert" class="mt-6 text-red-700">{{ errorMessage }}</p>
    <p v-else-if="eventTypes.length === 0" class="mt-6 text-slate-500">
      No event types are available right now.
    </p>
    <ul v-else class="mt-6 grid gap-4 sm:grid-cols-2">
      <li v-for="eventType in eventTypes" :key="eventType.id">
        <RouterLink
          :to="{ name: 'book', params: { eventTypeId: eventType.id } }"
          class="block rounded-lg border border-slate-200 bg-white p-4 hover:border-sky-400"
        >
          <h2 class="text-lg font-semibold">{{ eventType.title }}</h2>
          <p class="mt-1 text-sm text-slate-600">{{ eventType.description }}</p>
          <p class="mt-2 text-sm font-medium text-slate-700">{{ eventType.durationMinutes }} min</p>
        </RouterLink>
      </li>
    </ul>
  </section>
</template>
