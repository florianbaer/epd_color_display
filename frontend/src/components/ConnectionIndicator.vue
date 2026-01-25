<script setup lang="ts">
defineProps<{
  connected: boolean
}>()
</script>

<template>
  <span
    class="ws-indicator"
    :class="{ connected }"
    :title="connected ? 'Connected' : 'Disconnected'"
  />
</template>
