<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useImageStore } from '../stores/imageStore'
import ImageGallery from '../components/gallery/ImageGallery.vue'
import UploadGallery from '../components/gallery/UploadGallery.vue'
import ImageModal from '../components/gallery/ImageModal.vue'

type GalleryTab = 'feed' | 'uploads'

const imageStore = useImageStore()
const galleryTab = ref<GalleryTab>('feed')
const scrollContainer = ref<HTMLElement | null>(null)

function onScroll() {
  const el = scrollContainer.value
  if (!el || galleryTab.value !== 'feed') return
  // Trigger load when within 300px of the bottom
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 300) {
    imageStore.loadMoreFeed()
  }
}

function handleTabChange(tab: GalleryTab) {
  galleryTab.value = tab
  if (tab === 'feed') {
    imageStore.loadFeed()
  } else {
    imageStore.loadUploads()
  }
}

onMounted(() => {
  imageStore.loadFeed()
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Sub-tab navigation -->
    <div class="flex border-b border-gray-200 px-4 pt-2">
      <button
        class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
        :class="galleryTab === 'feed'
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-500 hover:text-gray-700'"
        @click="handleTabChange('feed')"
      >
        Feed
      </button>
      <button
        class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
        :class="galleryTab === 'uploads'
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-500 hover:text-gray-700'"
        @click="handleTabChange('uploads')"
      >
        Uploads
      </button>
    </div>

    <!-- Scrollable content — scroll event triggers pagination -->
    <div
      ref="scrollContainer"
      class="flex-1 overflow-y-auto min-h-0"
      @scroll.passive="onScroll"
    >
      <ImageGallery v-if="galleryTab === 'feed'" />
      <UploadGallery v-else />
    </div>

    <ImageModal
      v-if="imageStore.selectedImage"
      :image="imageStore.selectedImage"
      @close="imageStore.closeModal"
    />
  </div>
</template>
