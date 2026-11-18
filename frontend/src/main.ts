import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'

import App from './App.vue'

import Home from './views/Home.vue'
import WhatsApp from './views/Whatsapp.vue'
import SMS from './views/SMS.vue'
import Email from './views/Email.vue'
import Instagram from './views/Instagram.vue'
import Blogs from './views/Blogs.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/whatsapp', component: WhatsApp },
    { path: '/sms', component: SMS },
    { path: '/email', component: Email },
    { path: '/instagram', component: Instagram },
    { path: '/blogs', component: Blogs },
  ],
})

createApp(App)
  .use(router)
  .mount('#app')