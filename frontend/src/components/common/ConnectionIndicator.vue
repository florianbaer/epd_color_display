<script setup lang="ts">
defineProps<{
  connected: boolean
}>()
</script>

<template>
  <span
    class="inline-block w-2 h-2 rounded-full"
    :class="connected ? 'bg-success' : 'bg-error'"
    :title="connected ? 'Connected' : 'Disconnected'"
  />
</template>
