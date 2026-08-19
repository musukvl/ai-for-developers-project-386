import { createRouter, createWebHistory } from "vue-router";

import CalendarView from "../shell/CalendarView.vue";
import RootView from "../shell/RootView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "root", component: RootView },
    { path: "/cal/:ownerId", name: "calendar", component: CalendarView, props: true },
  ],
});
