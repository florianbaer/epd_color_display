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
  <article class="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
    <!-- Post header -->
    <div class="px-4 py-3 border-b border-gray-100">
      <p class="text-sm text-gray-800 leading-relaxed whitespace-pre-line">
        {{ group.prompt || 'Prompt not recorded' }}
      </p>
      <time class="text-xs text-gray-400 mt-1 block">{{ formatDate(group.generated_at) }}</time>
    </div>

    <!-- Images -->
    <div
      v-if="group.images.length === 1"
      class="cursor-pointer"
      @click="handleImageClick(group.images[0])"
    >
      <img
        :src="group.images[0].url"
        :alt="group.images[0].filename"
        loading="lazy"
        class="w-full block"
      />
    </div>

    <div
      v-else
      class="flex overflow-x-auto gap-1 snap-x snap-mandatory"
    >
      <div
        v-for="img in group.images"
        :key="img.filename"
        class="flex-shrink-0 snap-start cursor-pointer"
        :style="{ width: group.images.length === 2 ? '50%' : '80%' }"
        @click="handleImageClick(img)"
      >
        <img
          :src="img.url"
          :alt="img.filename"
          loading="lazy"
          class="w-full block"
        />
      </div>
    </div>

    <!-- Footer with image count -->
    <div v-if="group.images.length > 1" class="px-4 py-2 text-xs text-gray-400 border-t border-gray-100">
      {{ group.images.length }} images
    </div>
  </article>
</template>
