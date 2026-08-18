import { createRouter, createWebHistory } from 'vue-router'
import AppRoot from './AppRoot.vue'
import CalendarRoute from './CalendarRoute.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: AppRoot }, { path: '/cal/:ownerId', component: CalendarRoute }],
})
