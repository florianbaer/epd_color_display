<script setup lang="ts">
import type { GenerationStatus } from '../types'

defineProps<{
  status: GenerationStatus
}>()
</script>

<template>
  <div class="status-message" :class="`status-${status.status}`">
    <strong>Status:</strong> {{ status.message }}
  </div>
</template>
