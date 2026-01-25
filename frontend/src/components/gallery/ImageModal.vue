<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { ImageInfo } from '../../types'
import { useImageStore } from '../../stores/imageStore'
import { useStatusStore } from '../../stores/statusStore'

const props = defineProps<{
  image: ImageInfo
}>()

const emit = defineEmits<{
  close: []
}>()

const imageStore = useImageStore()
const statusStore = useStatusStore()

const displayFeedback = ref<{ show: boolean; type: string; message: string }>({
  show: false,
  type: '',
  message: '',
})

function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleString()
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function showFeedback(type: string, message: string) {
  displayFeedback.value = { show: true, type, message }
  setTimeout(() => {
    displayFeedback.value.show = false
  }, 5000)
}

async function handleDisplayOnEpaper() {
  const result = await imageStore.displayOnEpaper(props.image.filename)
  if (result.success) {
    showFeedback('success', 'Sending to e-paper display...')
  } else {
    showFeedback('error', result.message)
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div
    class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-5"
    @click.self="emit('close')"
  >
    <div class="max-w-[90vw] max-h-[90vh] relative bg-white rounded-lg overflow-hidden shadow-2xl">
      <button
        class="absolute top-3 right-3 bg-white/90 hover:bg-white rounded-full w-8 h-8 text-lg flex items-center justify-center shadow-md transition-all z-10"
        @click="emit('close')"
      >
        &times;
      </button>

      <img
        :src="image.url"
        :alt="image.filename"
        class="max-w-full max-h-[70vh] block"
      />

      <div class="p-4 bg-gray-50 border-t border-gray-200">
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0 flex-1">
            <div class="text-sm font-medium text-gray-800 truncate">{{ image.filename }}</div>
            <div class="text-xs text-gray-500 mt-1">
              {{ formatDate(image.created_at) }} &middot; {{ formatSize(image.size_bytes) }}
            </div>
          </div>

          <div class="flex flex-col items-end gap-2">
            <button
              class="btn btn-primary text-sm px-4 py-2"
              :disabled="statusStore.generating || imageStore.displayingImage"
              @click="handleDisplayOnEpaper"
            >
              <template v-if="imageStore.displayingImage">
                <span class="inline-block w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2 align-middle"></span>
                Sending...
              </template>
              <template v-else>
                Display on E-Paper
              </template>
            </button>

            <span
              v-if="displayFeedback.show"
              class="text-xs transition-opacity duration-300"
              :class="displayFeedback.type === 'success' ? 'text-success' : 'text-error'"
            >
              {{ displayFeedback.message }}
            </span>
          </div>
        </div>

        <div
          v-if="statusStore.generating"
          class="mt-3 status-message status-running text-xs"
        >
          {{ statusStore.status.message }}
        </div>
      </div>
    </div>
  </div>
</template>
