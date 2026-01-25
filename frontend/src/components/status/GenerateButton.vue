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
    class="btn btn-primary"
    :disabled="loading"
    @click="emit('generate')"
  >
    <span
      v-if="loading"
      class="inline-block w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2 align-middle"
    ></span>
    {{ loading ? (statusMessage || 'Generating...') : 'Generate & Display on E-Paper' }}
  </button>
</template>
