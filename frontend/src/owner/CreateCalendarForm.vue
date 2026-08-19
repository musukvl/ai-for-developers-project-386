<script setup lang="ts">
/**
 * Creating a calendar is owner logic. This component is mounted both on the
 * root page (once a name is entered) and on `/cal/:ownerId` when the owner's
 * own calendar does not exist yet.
 */
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import { ApiError } from "../api/client";
import { useUserName } from "../shell/useUserName";
import { createCalendar } from "./api";

const props = defineProps<{ ownerId: string }>();

const { hasCalendar, statusLoaded, markHasCalendar } = useUserName();
const router = useRouter();

const isCreating = ref(false);
const errorMessage = ref("");

const calendarPath = computed(() => `/cal/${props.ownerId}`);

async function handleCreate(): Promise<void> {
  errorMessage.value = "";
  isCreating.value = true;
  try {
    const result = await createCalendar(props.ownerId);
    markHasCalendar();
    await router.push(result.calendarUrl);
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : "Could not create the calendar. Please try again.";
  } finally {
    isCreating.value = false;
  }
}
</script>

<template>
  <section class="mx-auto max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    <p v-if="!statusLoaded" class="text-sm text-slate-500">Loading your account…</p>

    <template v-else-if="hasCalendar">
      <h2 class="text-xl font-semibold text-slate-900">Welcome back, {{ ownerId }}</h2>
      <p class="mt-2 text-sm text-slate-600">You already have a calendar.</p>
      <RouterLink
        :to="calendarPath"
        class="mt-4 inline-block rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-500"
      >
        Go to my calendar
      </RouterLink>
    </template>

    <template v-else>
      <h2 class="text-xl font-semibold text-slate-900">Create your calendar</h2>
      <p class="mt-2 text-sm text-slate-600">
        Your calendar will be published at <code class="rounded bg-slate-100 px-1">/cal/{{ ownerId }}</code>
        so others can book time with you.
      </p>
      <p v-if="errorMessage" role="alert" class="mt-3 text-sm text-red-600">{{ errorMessage }}</p>
      <button
        type="button"
        :disabled="isCreating"
        class="mt-4 rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-50"
        @click="handleCreate"
      >
        {{ isCreating ? "Creating…" : "Create calendar" }}
      </button>
    </template>
  </section>
</template>
