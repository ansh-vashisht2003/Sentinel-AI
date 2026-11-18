
<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const channels = [
  { name: 'WhatsApp', path: '/whatsapp' },
  { name: 'SMS', path: '/sms' },
  { name: 'Email', path: '/email' },
  { name: 'Instagram', path: '/instagram' },
]

const isActive = (path: string) => route.path === path
</script>

<template>
  <header
    class="sticky top-0 z-50 w-full border-b border-slate-800 bg-[#08111f]/95 backdrop-blur-xl"
  >
    <div class="flex h-[76px] items-center justify-between gap-6 px-8">

      <!-- Brand -->
      <button
        @click="router.push('/')"
        class="flex shrink-0 flex-col text-left"
      >
        <h1 class="text-xl font-extrabold tracking-wider text-white">
          SENTINEL <span class="text-cyan-400">AI</span>
        </h1>
        <p class="mt-0.5 text-[9px] font-semibold tracking-[3px] text-slate-500">
          THREAT INTELLIGENCE
        </p>
      </button>

      <!-- Navigation -->
      <nav class="flex items-center gap-2">
        <button
          v-for="channel in channels"
          :key="channel.name"
          @click="router.push(channel.path)"
          :aria-pressed="isActive(channel.path)"
          class="relative rounded-lg px-5 py-3 text-sm font-semibold transition-all duration-200"
          :class="isActive(channel.path)
            ? 'bg-cyan-400/10 text-cyan-400'
            : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          {{ channel.name }}

          <span
            v-if="isActive(channel.path)"
            class="absolute bottom-0 left-1/2 h-[2px] w-8 -translate-x-1/2 rounded-full bg-cyan-400"
          ></span>
        </button>
      </nav>

      <!-- Blogs -->
      <button
        @click="router.push('/blogs')"
        class="shrink-0 rounded-lg border border-slate-700 px-5 py-2.5 text-sm font-semibold transition-all duration-200"
        :class="route.path === '/blogs'
          ? 'border-cyan-400 bg-cyan-400/10 text-cyan-400'
          : 'text-slate-300 hover:border-cyan-400 hover:bg-cyan-400/10 hover:text-cyan-400'"
      >
        Blogs
      </button>

    </div>
  </header>
</template>
