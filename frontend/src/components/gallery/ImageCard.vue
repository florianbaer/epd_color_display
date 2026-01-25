<script setup lang="ts">
import type { ImageInfo } from '../../types'

defineProps<{
  image: ImageInfo
}>()

const emit = defineEmits<{
  click: [image: ImageInfo]
}>()

function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleString()
}
</script>

<template>
  <div
    class="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden cursor-pointer transition-all duration-200 hover:-translate-y-1 hover:shadow-lg hover:border-primary"
    @click="emit('click', image)"
  >
    <img
      :src="image.url"
      :alt="image.filename"
      loading="lazy"
      class="w-full h-36 object-cover block"
    />
    <div class="p-3">
      <div class="text-xs text-gray-700 truncate">{{ image.filename }}</div>
      <div class="text-[11px] text-gray-400 mt-1">{{ formatDate(image.created_at) }}</div>
    </div>
  </div>
</template>
