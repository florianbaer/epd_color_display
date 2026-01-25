<script setup lang="ts">
import type { TabType } from '../../types'

defineProps<{
  activeTab: TabType
}>()

const emit = defineEmits<{
  'update:activeTab': [tab: TabType]
}>()

function switchTab(tab: TabType) {
  emit('update:activeTab', tab)
}
</script>

<template>
  <nav class="flex border-b border-gray-200 bg-gray-50">
    <button
      class="flex-1 px-6 py-4 text-sm font-semibold text-gray-500 border-b-2 border-transparent transition-all duration-200 hover:text-primary hover:bg-primary/5"
      :class="{ 'text-primary border-primary bg-white': activeTab === 'editor' }"
      @click="switchTab('editor')"
    >
      Editor
    </button>
    <button
      class="flex-1 px-6 py-4 text-sm font-semibold text-gray-500 border-b-2 border-transparent transition-all duration-200 hover:text-primary hover:bg-primary/5"
      :class="{ 'text-primary border-primary bg-white': activeTab === 'gallery' }"
      @click="switchTab('gallery')"
    >
      Gallery
    </button>
  </nav>
</template>
