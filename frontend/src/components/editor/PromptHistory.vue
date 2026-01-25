<script setup lang="ts">
import type { PromptHistoryItem } from '../../types'

defineProps<{
  prompts: PromptHistoryItem[]
}>()

const emit = defineEmits<{
  select: [prompt: string]
}>()
</script>

<template>
  <div class="flex flex-col gap-2">
    <div v-if="prompts.length === 0" class="bg-gray-50 border-l-4 border-primary p-4 rounded text-sm text-gray-500">
      No prompt history yet.
    </div>
    <div
      v-for="item in prompts"
      :key="item.timestamp"
      class="bg-gray-50 border border-gray-200 rounded-lg p-3 cursor-pointer transition-all duration-200 hover:bg-gray-100 hover:border-primary"
      @click="emit('select', item.prompt)"
    >
      <div class="text-xs text-gray-400 mb-1">{{ item.timestamp }}</div>
      <div class="text-sm text-gray-700 truncate">{{ item.prompt }}</div>
    </div>
  </div>
</template>
