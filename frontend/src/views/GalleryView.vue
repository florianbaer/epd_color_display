<script setup lang="ts">
import { onMounted } from 'vue'
import { useImageStore } from '../stores/imageStore'
import ImageGallery from '../components/gallery/ImageGallery.vue'
import ImageModal from '../components/gallery/ImageModal.vue'

const imageStore = useImageStore()

onMounted(() => {
  imageStore.loadImages()
})
</script>

<template>
  <div>
    <section class="p-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Generated Images</h2>
      <ImageGallery />
    </section>

    <ImageModal
      v-if="imageStore.selectedImage"
      :image="imageStore.selectedImage"
      @close="imageStore.closeModal"
    />
  </div>
</template>
