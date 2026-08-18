<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../shared/apiClient'
import { rememberUserName } from './useUserName'

const emit = defineEmits<{ entered: [] }>()
const name = ref('')
const error = ref('')
async function submit(): Promise<void> {
  error.value = ''
  try {
    const response = await api<{ name: string }>('/users', { method: 'POST', body: JSON.stringify({ name: name.value }) })
    rememberUserName(response.name)
    emit('entered')
  } catch (reason) { error.value = reason instanceof Error ? reason.message : 'Could not enter name.' }
}
</script>
<template>
  <form class="mx-auto mt-20 max-w-md space-y-4 rounded bg-white p-6 shadow" @submit.prevent="submit">
    <h1 class="text-2xl font-bold">Calls Calendar</h1><p>Enter your name to manage or book meetings.</p>
    <label class="block">Name <input v-model="name" class="mt-1 w-full" data-testid="name-input" required /></label>
    <p v-if="error" class="text-red-700">{{ error }}</p><button data-testid="enter-name">Continue</button>
  </form>
</template>
