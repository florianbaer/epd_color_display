<script setup lang="ts">
import type { GenerationStatus } from '../../types'

defineProps<{
  status: GenerationStatus
}>()
</script>

<template>
  <div class="status-message mt-4" :class="`status-${status.status}`">
    <strong>Status:</strong> {{ status.message }}
  </div>
</template>
