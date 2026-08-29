<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="border-b border-slate-200 bg-white">
      <nav class="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <RouterLink to="/" class="font-semibold">Calls Calendar</RouterLink>
        <RouterLink to="/owner" class="text-sm font-medium text-slate-700 hover:text-sky-700">
          Owner
        </RouterLink>
      </nav>
    </header>
    <main class="mx-auto max-w-5xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
