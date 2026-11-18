
<script setup lang="ts">
import Status from './components/status/status.vue'
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-[#08111f] text-white">
    <Status />

    <!-- Dynamically displays the selected route -->
    <RouterView />
  </div>
</template>
