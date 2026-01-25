<script setup lang="ts">
import { useConnectionStore } from '../../stores/connectionStore'
import ConnectionIndicator from '../common/ConnectionIndicator.vue'

const connectionStore = useConnectionStore()
</script>

<template>
  <header class="bg-gradient-primary text-white py-8 px-6 text-center">
    <h1 class="text-2xl font-semibold mb-2 flex items-center justify-center gap-2">
      E-Paper Display Image Generator
      <ConnectionIndicator :connected="connectionStore.connected" />
    </h1>
    <div class="opacity-90 text-sm">Powered by Gemini AI</div>
  </header>
</template>
