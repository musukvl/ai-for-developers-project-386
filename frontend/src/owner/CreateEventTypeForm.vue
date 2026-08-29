<script setup lang="ts">
import { reactive, ref } from "vue";

import { ApiError } from "../api/client";
import { createEventType } from "./api";

const emit = defineEmits<{
  (event: "created"): void;
}>();

const form = reactive({
  id: "",
  title: "",
  description: "",
  durationMinutes: 30,
});
const submitting = ref(false);
const errorMessage = ref<string | null>(null);

async function submit(): Promise<void> {
  submitting.value = true;
  errorMessage.value = null;
  try {
    await createEventType({
      id: form.id.trim(),
      title: form.title.trim(),
      description: form.description,
      durationMinutes: Number(form.durationMinutes),
    });
    form.id = "";
    form.title = "";
    form.description = "";
    form.durationMinutes = 30;
    emit("created");
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "Could not create event type.";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <form class="rounded-lg border border-slate-200 bg-white p-4" @submit.prevent="submit">
    <h2 class="text-lg font-semibold">Create event type</h2>
    <p v-if="errorMessage" role="alert" class="mt-2 text-sm text-red-700">{{ errorMessage }}</p>
    <div class="mt-3 grid gap-3 sm:grid-cols-2">
      <label class="block text-sm">
        Id
        <input
          v-model="form.id"
          required
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
        />
      </label>
      <label class="block text-sm">
        Title
        <input
          v-model="form.title"
          required
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
        />
      </label>
      <label class="block text-sm sm:col-span-2">
        Description
        <textarea
          v-model="form.description"
          required
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
        />
      </label>
      <label class="block text-sm">
        Duration in minutes
        <input
          v-model.number="form.durationMinutes"
          type="number"
          min="1"
          required
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
        />
      </label>
    </div>
    <button
      type="submit"
      class="mt-4 rounded-md bg-sky-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"
      :disabled="submitting"
    >
      Create event type
    </button>
  </form>
</template>
