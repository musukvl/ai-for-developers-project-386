<script setup lang="ts">
/**
 * The shell resolves the role by comparing the entered name with `ownerId`
 * in the URL, then mounts the owner or visitor module. There is no backend
 * role or session endpoint; this comparison is the entire routing decision.
 */
import { computed } from "vue";

import OwnerCalendarPage from "../owner/OwnerCalendarPage.vue";
import VisitorCalendarPage from "../visitor/VisitorCalendarPage.vue";
import { useUserName } from "./useUserName";

const props = defineProps<{ ownerId: string }>();

const { userName } = useUserName();

const isOwner = computed(() => userName.value === props.ownerId);
</script>

<template>
  <OwnerCalendarPage v-if="isOwner" :owner-id="ownerId" />
  <VisitorCalendarPage v-else :owner-id="ownerId" />
</template>
