<script setup lang="ts">
import type { PromptHistoryItem } from '../types'

defineProps<{
  prompts: PromptHistoryItem[]
}>()

const emit = defineEmits<{
  select: [prompt: string]
}>()
</script>

<template>
  <div class="prompt-history">
    <div v-if="prompts.length === 0" class="info-box">
      No prompt history yet.
    </div>
    <div
      v-for="item in prompts"
      :key="item.timestamp"
      class="prompt-history-item"
      @click="emit('select', item.prompt)"
    >
      <div class="timestamp">{{ item.timestamp }}</div>
      <div class="prompt-text">{{ item.prompt }}</div>
    </div>
  </div>
</template>
