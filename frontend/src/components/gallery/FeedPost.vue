<script setup lang="ts">
import type { FeedGroup, ImageInfo } from '../../types'
import { useImageStore } from '../../stores/imageStore'

defineProps<{
  group: FeedGroup
}>()

const imageStore = useImageStore()

function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleString()
}

function handleImageClick(img: FeedGroup['images'][number]) {
  // Convert FeedImageInfo to ImageInfo for the modal
  imageStore.selectImage({
    filename: img.filename,
    path: '',
    url: img.url,
    created_at: img.created_at,
    size_bytes: img.size_bytes,
  } as ImageInfo)
}
</script>

<template>
  <article>
    <!-- Sticky prompt header -->
    <div class="sticky top-0 z-10 bg-white/95 backdrop-blur-sm border-b border-gray-100 px-4 py-3 shadow-sm">
      <p class="text-sm font-medium text-gray-800 leading-relaxed whitespace-pre-line">
        {{ group.prompt || 'Prompt not recorded' }}
      </p>
      <time class="text-xs text-gray-400 mt-0.5 block">{{ formatDate(group.generated_at) }}</time>
    </div>

    <!-- Vertically stacked images -->
    <div
      v-for="img in group.images"
      :key="img.filename"
      class="w-full bg-black flex items-center justify-center cursor-pointer"
      style="max-height: 80vh;"
      @click="handleImageClick(img)"
    >
      <img
        :src="img.url"
        :alt="img.filename"
        loading="lazy"
        style="width: 100%; max-height: 80vh; object-fit: contain; display: block;"
      />
    </div>
  </article>
</template>
