import { createApp } from 'vue'
import App from './shell/App.vue'
import router from './shell/router'
import './style.css'

createApp(App).use(router).mount('#app')
