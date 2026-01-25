import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ImageInfo } from '../types'
import * as api from '../services/api'
import { useStatusStore } from './statusStore'

export const useImageStore = defineStore('image', () => {
  const images = ref<ImageInfo[]>([])
  const selectedImage = ref<ImageInfo | null>(null)
  const displayingImage = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadImages(limit: number = 50) {
    loading.value = true
    error.value = null
    try {
      images.value = await api.getImages(limit)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load images'
    } finally {
      loading.value = false
    }
  }

  function selectImage(image: ImageInfo | null) {
    selectedImage.value = image
  }

  function closeModal() {
    selectedImage.value = null
  }

  async function displayOnEpaper(filename: string): Promise<{ success: boolean; message: string }> {
    const statusStore = useStatusStore()

    if (statusStore.generating) {
      return { success: false, message: 'Generation already in progress' }
    }

    displayingImage.value = true
    error.value = null

    try {
      const result = await api.displayImage(filename)
      statusStore.startPolling()
      return result
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to display image'
      error.value = message
      return { success: false, message }
    } finally {
      displayingImage.value = false
    }
  }

  return {
    images,
    selectedImage,
    displayingImage,
    loading,
    error,
    loadImages,
    selectImage,
    closeModal,
    displayOnEpaper,
  }
})
