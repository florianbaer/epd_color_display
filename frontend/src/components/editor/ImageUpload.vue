<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useImageStore } from '../../stores/imageStore'

const imageStore = useImageStore()

type FeedbackType = 'success' | 'error'

const ALLOWED_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp', 'image/gif'])
const MAX_SIZE = 20 * 1024 * 1024

const label = ref('Uploaded')
const selectedFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const feedback = ref<{ show: boolean; type: FeedbackType; message: string }>({
  show: false,
  type: 'success',
  message: '',
})

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  if (!file) return

  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function showFeedback(type: FeedbackType, message: string) {
  feedback.value = { show: true, type, message }
  setTimeout(() => { feedback.value.show = false }, 3000)
}

async function handleUpload() {
  if (!selectedFile.value) return

  if (!ALLOWED_TYPES.has(selectedFile.value.type)) {
    showFeedback('error', 'Unsupported file type')
    return
  }
  if (selectedFile.value.size > MAX_SIZE) {
    showFeedback('error', 'File exceeds 20 MB limit')
    return
  }

  const trimmedLabel = label.value.trim() || 'Uploaded'
  const result = await imageStore.uploadImage(selectedFile.value, trimmedLabel)
  if (result.success) {
    showFeedback('success', 'Uploaded!')
    selectedFile.value = null
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value)
      previewUrl.value = null
    }
    if (fileInputRef.value) fileInputRef.value.value = ''
  } else {
    showFeedback('error', result.message)
  }
}

onUnmounted(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex gap-3 items-end">
      <div class="flex-1">
        <label class="text-xs text-gray-500 mb-1 block">Label (groups images in gallery)</label>
        <input
          v-model="label"
          type="text"
          placeholder="e.g. My photos"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"
        />
      </div>
      <button
        class="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors whitespace-nowrap"
        @click="fileInputRef?.click()"
      >
        Choose Image
      </button>
      <input
        ref="fileInputRef"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleFileChange"
      />
    </div>

    <div v-if="previewUrl" class="rounded-lg overflow-hidden border border-gray-200">
      <img :src="previewUrl" class="w-full max-h-48 object-contain bg-gray-50 block" alt="Preview" />
    </div>

    <div v-if="selectedFile" class="flex items-center gap-3">
      <span class="text-sm text-gray-500 truncate flex-1">{{ selectedFile.name }}</span>
      <button
        class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :disabled="imageStore.uploading"
        @click="handleUpload"
      >
        <span v-if="imageStore.uploading">Uploading...</span>
        <span v-else>Upload to Gallery</span>
      </button>
      <span
        v-if="feedback.show"
        class="text-sm"
        :class="feedback.type === 'success' ? 'text-green-600' : 'text-red-600'"
      >
        {{ feedback.message }}
      </span>
    </div>
  </div>
</template>
