<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { userName } from './useUserName'
import NameEntry from './NameEntry.vue'
import OwnerView from '../owner/OwnerView.vue'
import VisitorView from '../visitor/VisitorView.vue'

const route = useRoute()
const ownerId = computed(() => String(route.params.ownerId).toLowerCase())
</script>
<template><NameEntry v-if="!userName" @entered="() => {}" /><OwnerView v-else-if="userName === ownerId" :owner-id="ownerId" /><VisitorView v-else :owner-id="ownerId" /></template>
