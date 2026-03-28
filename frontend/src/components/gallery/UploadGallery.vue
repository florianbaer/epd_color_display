<script setup lang="ts">
import { useImageStore } from '../../stores/imageStore'

const imageStore = useImageStore()

function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleString()
}
</script>

<template>
  <div>
    <div v-if="imageStore.loading" class="p-8 text-sm text-gray-400 text-center">
      Loading uploads...
    </div>

    <div v-else-if="imageStore.uploadedImages.length === 0" class="text-center py-16 text-gray-400">
      <p class="text-base">No uploads yet.</p>
      <p class="mt-2 text-sm">Upload images in the Editor tab.</p>
    </div>

    <div v-else class="grid grid-cols-2 gap-1 p-1">
      <div
        v-for="img in imageStore.uploadedImages"
        :key="img.filename"
        class="cursor-pointer bg-black aspect-video overflow-hidden relative group"
        @click="imageStore.selectImage(img)"
      >
        <img
          :src="img.url"
          :alt="img.filename"
          loading="lazy"
          class="w-full h-full object-contain"
        />
        <div class="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity truncate">
          {{ formatDate(img.created_at) }}
        </div>
      </div>
    </div>
  </div>
</template>
