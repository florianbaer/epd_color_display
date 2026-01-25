<script setup lang="ts">
defineProps<{
  loading: boolean
  statusMessage?: string
}>()

const emit = defineEmits<{
  generate: []
}>()
</script>

<template>
  <button
    class="btn-primary"
    :disabled="loading"
    @click="emit('generate')"
  >
    <span v-if="loading" class="spinner"></span>
    {{ loading ? (statusMessage || 'Generating...') : 'Generate & Display on E-Paper' }}
  </button>
</template>
