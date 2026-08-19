<script setup lang="ts">
/**
 * The application shell: the name-entry gate lives here, not in the owner
 * or visitor module, per spec/implementation.md.
 */
import NameEntryView from "./shell/NameEntryView.vue";
import { useUserName } from "./shell/useUserName";

const { isSignedIn, userName } = useUserName();
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <RouterLink to="/" class="text-lg font-semibold text-slate-900">Calls Calendar</RouterLink>
        <span v-if="isSignedIn" class="text-sm text-slate-500">Signed in as {{ userName }}</span>
      </div>
    </header>
    <main class="mx-auto max-w-4xl px-4 py-6">
      <NameEntryView v-if="!isSignedIn" />
      <RouterView v-else />
    </main>
  </div>
</template>
