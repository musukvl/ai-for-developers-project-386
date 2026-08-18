<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../shared/apiClient'
import { userName } from '../shell/useUserName'
const emit = defineEmits<{ created: [url: string] }>()
const error = ref('')
async function create(): Promise<void> {
  try {
    const result = await api<{ calendarUrl: string }>('/calendars', { method: 'POST', body: JSON.stringify({ ownerId: userName.value }) })
    emit('created', result.calendarUrl)
  } catch (reason) { error.value = reason instanceof Error ? reason.message : 'Calendar creation failed.' }
}
</script>
<template><section class="space-y-4"><h1 class="text-2xl font-bold">Your calendar</h1><p>Create your public calendar to publish availability.</p><p v-if="error" class="text-red-700">{{ error }}</p><button data-testid="create-calendar" @click="create">Create calendar</button></section></template>
