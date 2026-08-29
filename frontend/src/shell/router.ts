import { createRouter, createWebHistory } from "vue-router";

import EventTypeCatalog from "../guest/EventTypeCatalog.vue";
import BookPage from "../guest/BookPage.vue";
import OwnerPage from "../owner/OwnerPage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "catalog", component: EventTypeCatalog },
    { path: "/book/:eventTypeId", name: "book", component: BookPage, props: true },
    { path: "/owner", name: "owner", component: OwnerPage },
  ],
});
