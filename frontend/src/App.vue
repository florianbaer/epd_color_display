<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import type { PromptHistoryItem, TabType, WebSocketMessage } from './types'
import { useApi } from './composables/useApi'
import { useWebSocket } from './composables/useWebSocket'
import { useStatus } from './composables/useStatus'

import ConnectionIndicator from './components/ConnectionIndicator.vue'
import PromptEditor from './components/PromptEditor.vue'
import PromptHistory from './components/PromptHistory.vue'
import GenerateButton from './components/GenerateButton.vue'
import StatusDisplay from './components/StatusDisplay.vue'
import ImageGallery from './components/ImageGallery.vue'

const {
  getCurrentPrompt,
  savePrompt,
  getPromptHistory,
  startGeneration,
} = useApi()

const { status, startPolling, refreshStatus } = useStatus()

// State
const prompt = ref('')
const promptHistory = ref<PromptHistoryItem[]>([])
const activeTab = ref<TabType>('editor')
const saveFeedback = ref<{ show: boolean; type: string; message: string }>({
  show: false,
  type: '',
  message: '',
})
const generating = ref(false)
const galleryRef = ref<InstanceType<typeof ImageGallery> | null>(null)

// WebSocket handler
function handleWebSocketMessage(message: WebSocketMessage) {
  if (message.type === 'prompt_updated' && message.prompt) {
    prompt.value = message.prompt
    showFeedback('success', 'Prompt updated by another user')
    loadHistory()
  }
}

const { connected } = useWebSocket(handleWebSocketMessage)

// Computed
const isRunning = computed(() => status.value.status === 'running')

// Methods
function showFeedback(type: string, message: string) {
  saveFeedback.value = { show: true, type, message }
  setTimeout(() => {
    saveFeedback.value.show = false
  }, 3000)
}

async function loadPrompt() {
  try {
    prompt.value = await getCurrentPrompt()
  } catch (err) {
    console.error('Failed to load prompt:', err)
  }
}

async function loadHistory() {
  try {
    promptHistory.value = await getPromptHistory(3)
  } catch (err) {
    console.error('Failed to load history:', err)
  }
}

async function handleSavePrompt(newPrompt: string) {
  try {
    await savePrompt(newPrompt)
    showFeedback('success', 'Saved!')
    await loadHistory()
  } catch (err) {
    showFeedback('error', 'Failed to save')
    console.error('Failed to save prompt:', err)
  }
}

function handleSelectPrompt(selectedPrompt: string) {
  prompt.value = selectedPrompt
}

async function handleGenerate() {
  try {
    generating.value = true
    await startGeneration()
    startPolling(2000)

    // Wait for completion
    const checkComplete = setInterval(async () => {
      await refreshStatus()
      if (status.value.status !== 'running') {
        generating.value = false
        clearInterval(checkComplete)

        // Refresh gallery if generation was successful
        if (status.value.status === 'complete' && galleryRef.value) {
          galleryRef.value.refresh()
        }

        // Reset status after a delay
        if (status.value.status === 'complete') {
          setTimeout(async () => {
            status.value = { status: 'idle', message: 'Ready' }
          }, 5000)
        }
      }
    }, 2000)
  } catch (err: unknown) {
    generating.value = false
    const message = err instanceof Error ? err.message : 'Unknown error'

    if (message.includes('409')) {
      alert('Generation already in progress. Please wait.')
    } else {
      alert('Failed to start generation: ' + message)
    }
  }
}

function switchTab(tab: TabType) {
  activeTab.value = tab
  if (tab === 'gallery' && galleryRef.value) {
    galleryRef.value.refresh()
  }
}

// Initialize
onMounted(async () => {
  await Promise.all([loadPrompt(), loadHistory(), refreshStatus()])

  // If already running, start polling
  if (status.value.status === 'running') {
    generating.value = true
    startPolling(2000)
  }
})
</script>

<template>
  <div class="container">
    <header>
      <h1>
        E-Paper Display Image Generator
        <ConnectionIndicator :connected="connected" />
      </h1>
      <div class="subtitle">Powered by Gemini AI</div>
    </header>

    <!-- Tab Navigation -->
    <nav class="tab-nav">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'editor' }"
        @click="switchTab('editor')"
      >
        Editor
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'gallery' }"
        @click="switchTab('gallery')"
      >
        Gallery
      </button>
    </nav>

    <!-- Editor Tab -->
    <template v-if="activeTab === 'editor'">
      <section>
        <h2>Edit Prompt</h2>
        <PromptEditor
          v-model="prompt"
          :max-length="1000"
          @save="handleSavePrompt"
        >
          <template #feedback>
            <span
              class="feedback"
              :class="[saveFeedback.type, { show: saveFeedback.show }]"
            >
              {{ saveFeedback.type === 'success' ? '&#10003;' : '&#10007;' }}
              {{ saveFeedback.message }}
            </span>
          </template>
        </PromptEditor>
      </section>

      <section>
        <h2>Recent Prompts</h2>
        <PromptHistory
          :prompts="promptHistory"
          @select="handleSelectPrompt"
        />
      </section>

      <section>
        <h2>Generate Image</h2>
        <GenerateButton
          :loading="generating || isRunning"
          :status-message="isRunning ? status.message : undefined"
          @generate="handleGenerate"
        />
        <StatusDisplay :status="status" />
        <div class="info-box">
          Image generation typically takes 20-45 seconds.
          The page will update automatically during the process.
        </div>
      </section>
    </template>

    <!-- Gallery Tab -->
    <template v-else-if="activeTab === 'gallery'">
      <section>
        <h2>Generated Images</h2>
        <ImageGallery ref="galleryRef" />
      </section>
    </template>
  </div>
</template>
