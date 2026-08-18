<script setup lang="ts">
import { userName } from './useUserName'
import NameEntry from './NameEntry.vue'
import CreateCalendarForm from '../owner/CreateCalendarForm.vue'
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
<template><NameEntry v-if="!userName" @entered="() => {}" /><CreateCalendarForm v-else @created="router.push" /></template>
