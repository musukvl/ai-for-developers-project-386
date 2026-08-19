<script setup lang="ts">
/**
 * The root page mounts the owner module once a name is entered: creating a
 * calendar is owner logic, so the shell delegates to it rather than
 * rendering a create form itself.
 */
import { onMounted } from "vue";

import CreateCalendarForm from "../owner/CreateCalendarForm.vue";
import { useUserName } from "./useUserName";

const { userName, refreshStatus } = useUserName();

onMounted(() => {
  void refreshStatus();
});
</script>

<template>
  <CreateCalendarForm :owner-id="userName" />
</template>
