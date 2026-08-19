<script setup lang="ts">
import { ref } from "vue";

import { ApiError } from "../api/client";
import { useUserName } from "./useUserName";

const { signIn } = useUserName();

const nameInput = ref("");
const isSubmitting = ref(false);
const errorMessage = ref("");

async function handleSubmit(): Promise<void> {
  errorMessage.value = "";
  isSubmitting.value = true;
  try {
    await signIn(nameInput.value);
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <section class="mx-auto mt-12 max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
    <h2 class="text-xl font-semibold text-slate-900">Welcome to Calls Calendar</h2>
    <p class="mt-2 text-sm text-slate-600">
      Enter your name to create your own calendar or to book time on someone else's. There is no
      password &mdash; the same name always means the same user.
    </p>
    <form class="mt-4 space-y-3" @submit.prevent="handleSubmit">
      <div>
        <label class="block text-sm font-medium text-slate-700" for="user-name">Your name</label>
        <input
          id="user-name"
          v-model="nameInput"
          type="text"
          required
          autocomplete="off"
          placeholder="e.g. alex"
          class="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
        />
      </div>
      <p v-if="errorMessage" role="alert" class="text-sm text-red-600">{{ errorMessage }}</p>
      <button
        type="submit"
        :disabled="isSubmitting || nameInput.trim().length === 0"
        class="w-full rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {{ isSubmitting ? "Please wait…" : "Continue" }}
      </button>
    </form>
  </section>
</template>
