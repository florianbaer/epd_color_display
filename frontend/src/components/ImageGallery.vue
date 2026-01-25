<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ImageInfo } from '../types'
import { useApi } from '../composables/useApi'

const { getImages, loading } = useApi()

const images = ref<ImageInfo[]>([])
const selectedImage = ref<ImageInfo | null>(null)

async function loadImages() {
  try {
    images.value = await getImages(50)
  } catch (err) {
    console.error('Failed to load images:', err)
  }
}

function openModal(image: ImageInfo) {
  selectedImage.value = image
}

function closeModal() {
  selectedImage.value = null
}

function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleString()
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && selectedImage.value) {
    closeModal()
  }
}

onMounted(() => {
  loadImages()
  window.addEventListener('keydown', handleKeydown)
})

defineExpose({ refresh: loadImages })
</script>

<template>
  <div>
    <div v-if="loading" class="info-box">
      Loading images...
    </div>

    <div v-else-if="images.length === 0" class="empty-state">
      <p>No images generated yet.</p>
      <p>Generate an image to see it here!</p>
    </div>

    <div v-else class="gallery-grid">
      <div
        v-for="image in images"
        :key="image.filename"
        class="gallery-item"
        @click="openModal(image)"
      >
        <img :src="image.url" :alt="image.filename" loading="lazy" />
        <div class="gallery-item-info">
          <div class="filename">{{ image.filename }}</div>
          <div class="date">{{ formatDate(image.created_at) }}</div>
        </div>
      </div>
    </div>

    <!-- Modal/Lightbox -->
    <div
      v-if="selectedImage"
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div class="modal-content">
        <button class="modal-close" @click="closeModal">x</button>
        <img :src="selectedImage.url" :alt="selectedImage.filename" />
      </div>
    </div>
  </div>
</template>
