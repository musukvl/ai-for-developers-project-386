/**
 * The entered name, tab-scoped via `sessionStorage`, shared by the whole app.
 *
 * Module-scoped refs make this a singleton: every caller of `useUserName()`
 * sees the same reactive state, which matches "one entered name per tab".
 */

import { computed, ref } from "vue";

import { USER_NAME_STORAGE_KEY } from "../api/client";
import { enterName } from "./usersApi";

const userName = ref<string>(sessionStorage.getItem(USER_NAME_STORAGE_KEY) ?? "");
const hasCalendar = ref<boolean>(false);
const statusLoaded = ref<boolean>(false);

export function useUserName() {
  const isSignedIn = computed(() => userName.value.length > 0);

  async function signIn(rawName: string): Promise<void> {
    const result = await enterName(rawName);
    userName.value = result.name;
    hasCalendar.value = result.hasCalendar;
    statusLoaded.value = true;
    sessionStorage.setItem(USER_NAME_STORAGE_KEY, result.name);
  }

  async function refreshStatus(): Promise<void> {
    if (!userName.value) {
      return;
    }
    const result = await enterName(userName.value);
    hasCalendar.value = result.hasCalendar;
    statusLoaded.value = true;
  }

  function markHasCalendar(): void {
    hasCalendar.value = true;
  }

  return { userName, hasCalendar, statusLoaded, isSignedIn, signIn, refreshStatus, markHasCalendar };
}
