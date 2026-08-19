<script setup lang="ts">
/**
 * The root page mounts the owner module once a name is entered: creating a
 * calendar is owner logic, so the shell delegates to it rather than
 * rendering a create form itself.
 */
import { onMounted } from "vue";

import CreateCalendarForm from "../owner/CreateCalendarForm.vue";
import CalendarDirectory from "../shared/CalendarDirectory.vue";
import { useUserName } from "./useUserName";

const { userName, refreshStatus } = useUserName();

onMounted(() => {
  void refreshStatus();
});
</script>

<template>
  <div class="space-y-6">
    <CreateCalendarForm :owner-id="userName" />
    <CalendarDirectory :current-owner-id="userName" />
  </div>
</template>
