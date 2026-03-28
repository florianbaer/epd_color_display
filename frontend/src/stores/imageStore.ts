import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ImageInfo, FeedGroup } from '../types'
import * as api from '../services/api'
import { useStatusStore } from './statusStore'

export const useImageStore = defineStore('image', () => {
  const images = ref<ImageInfo[]>([])
  const feedGroups = ref<FeedGroup[]>([])
  const feedHasMore = ref(false)
  const feedLoadingMore = ref(false)
  const feedOffset = ref(0)
  const uploadedImages = ref<ImageInfo[]>([])
  const selectedImage = ref<ImageInfo | null>(null)
  const displayingImage = ref(false)
  const uploading = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const FEED_PAGE_SIZE = 10

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

  async function loadFeed() {
    loading.value = true
    error.value = null
    feedGroups.value = []
    feedHasMore.value = false
    feedOffset.value = 0
    try {
      const result = await api.getGalleryFeed(FEED_PAGE_SIZE, 0)
      feedGroups.value = result.groups
      feedHasMore.value = result.has_more
      feedOffset.value = result.groups.length
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load feed'
    } finally {
      loading.value = false
    }
  }

  async function loadMoreFeed() {
    if (!feedHasMore.value || feedLoadingMore.value) return
    feedLoadingMore.value = true
    // Snapshot offset at call time — prevents race if called concurrently
    const offset = feedOffset.value
    try {
      const result = await api.getGalleryFeed(FEED_PAGE_SIZE, offset)
      feedGroups.value.push(...result.groups)
      feedOffset.value = offset + result.groups.length
      feedHasMore.value = result.has_more
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load more items'
    } finally {
      feedLoadingMore.value = false
    }
  }

  async function loadUploads(limit: number = 100) {
    loading.value = true
    error.value = null
    try {
      uploadedImages.value = await api.getUploads(limit)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load uploads'
    } finally {
      loading.value = false
    }
  }

  async function uploadImage(file: File, label: string): Promise<{ success: boolean; message: string }> {
    uploading.value = true
    error.value = null
    try {
      const result = await api.uploadImage(file, label)
      // Backend auto-triggers EPD display — start polling so the UI shows progress
      const statusStore = useStatusStore()
      statusStore.startPolling()
      try {
        await loadUploads()
      } catch {
        console.warn('Failed to refresh uploads list after successful upload')
      }
      return { success: true, message: result.message }
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Upload failed'
      error.value = message
      return { success: false, message }
    } finally {
      uploading.value = false
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
    feedGroups,
    feedHasMore,
    feedLoadingMore,
    feedOffset,
    uploadedImages,
    selectedImage,
    displayingImage,
    uploading,
    loading,
    error,
    loadImages,
    loadFeed,
    loadMoreFeed,
    loadUploads,
    uploadImage,
    selectImage,
    closeModal,
    displayOnEpaper,
  }
})
