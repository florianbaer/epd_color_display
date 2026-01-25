<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { usePromptStore } from '../stores/promptStore'
import { useStatusStore } from '../stores/statusStore'
import { useImageStore } from '../stores/imageStore'
import PromptEditor from '../components/editor/PromptEditor.vue'
import PromptHistory from '../components/editor/PromptHistory.vue'
import GenerateButton from '../components/status/GenerateButton.vue'
import StatusDisplay from '../components/status/StatusDisplay.vue'

const promptStore = usePromptStore()
const statusStore = useStatusStore()
const imageStore = useImageStore()

const saveFeedback = ref<{ show: boolean; type: string; message: string }>({
  show: false,
  type: '',
  message: '',
})

const isRunning = computed(() => statusStore.generating)

function showFeedback(type: string, message: string) {
  saveFeedback.value = { show: true, type, message }
  setTimeout(() => {
    saveFeedback.value.show = false
  }, 3000)
}

async function handleSavePrompt() {
  const result = await promptStore.save()
  if (result.success) {
    showFeedback('success', 'Saved!')
  } else {
    showFeedback('error', 'Failed to save')
  }
}

function handleSelectPrompt(selectedPrompt: string) {
  promptStore.setPrompt(selectedPrompt)
}

async function handleGenerate() {
  const result = await statusStore.startGeneration()
  if (!result.success) {
    if (result.message.includes('409')) {
      alert('Generation already in progress. Please wait.')
    } else {
      alert('Failed to start generation: ' + result.message)
    }
  }
}

// Watch for generation completion to refresh gallery
watch(() => statusStore.status.status, (newStatus, oldStatus) => {
  if (oldStatus === 'running' && newStatus === 'complete') {
    imageStore.loadImages()
    // Reset status after a delay
    setTimeout(() => {
      statusStore.status.status = 'idle'
      statusStore.status.message = 'Ready'
    }, 5000)
  }
})

onMounted(async () => {
  await Promise.all([
    promptStore.loadCurrent(),
    promptStore.loadHistory(),
    statusStore.refresh(),
  ])

  // If already running, start polling
  if (statusStore.generating) {
    statusStore.startPolling()
  }
})
</script>

<template>
  <div>
    <section class="p-8 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Edit Prompt</h2>
      <PromptEditor
        v-model="promptStore.prompt"
        :max-length="1000"
        @save="handleSavePrompt"
      >
        <template #feedback>
          <span
            class="ml-3 text-sm transition-opacity duration-300"
            :class="[
              saveFeedback.type === 'success' ? 'text-success' : 'text-error',
              saveFeedback.show ? 'opacity-100' : 'opacity-0'
            ]"
          >
            {{ saveFeedback.type === 'success' ? '&#10003;' : '&#10007;' }}
            {{ saveFeedback.message }}
          </span>
        </template>
      </PromptEditor>
    </section>

    <section class="p-8 border-b border-gray-200">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Recent Prompts</h2>
      <PromptHistory
        :prompts="promptStore.history"
        @select="handleSelectPrompt"
      />
    </section>

    <section class="p-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Generate Image</h2>
      <GenerateButton
        :loading="isRunning"
        :status-message="isRunning ? statusStore.status.message : undefined"
        @generate="handleGenerate"
      />
      <StatusDisplay :status="statusStore.status" />
      <div class="mt-4 bg-gray-50 border-l-4 border-primary p-4 rounded text-sm text-gray-500">
        Image generation typically takes 20-45 seconds.
        The page will update automatically during the process.
      </div>
    </section>
  </div>
</template>
