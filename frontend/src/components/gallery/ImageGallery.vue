<script setup lang="ts">
import { useImageStore } from '../../stores/imageStore'
import ImageCard from './ImageCard.vue'
import type { ImageInfo } from '../../types'

const imageStore = useImageStore()

function handleImageClick(image: ImageInfo) {
  imageStore.selectImage(image)
}

defineExpose({ refresh: () => imageStore.loadImages() })
</script>

<template>
  <div>
    <div v-if="imageStore.loading" class="bg-gray-50 border-l-4 border-primary p-4 rounded text-sm text-gray-500">
      Loading images...
    </div>

    <div v-else-if="imageStore.images.length === 0" class="text-center py-10 text-gray-400">
      <p>No images generated yet.</p>
      <p class="mt-2">Generate an image to see it here!</p>
    </div>

    <div v-else class="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-4">
      <ImageCard
        v-for="image in imageStore.images"
        :key="image.filename"
        :image="image"
        @click="handleImageClick"
      />
    </div>
  </div>
</template>
