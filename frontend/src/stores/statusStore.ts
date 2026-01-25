import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GenerationStatus } from '../types'
import * as api from '../services/api'

export const useStatusStore = defineStore('status', () => {
  const status = ref<GenerationStatus>({
    status: 'idle',
    message: 'Ready',
  })

  let pollInterval: ReturnType<typeof setInterval> | null = null

  const generating = computed(() => status.value.status === 'running')
  const isIdle = computed(() => status.value.status === 'idle')
  const isComplete = computed(() => status.value.status === 'complete')
  const isError = computed(() => status.value.status === 'error')

  async function refresh() {
    try {
      status.value = await api.getStatus()
    } catch (e) {
      console.error('Failed to refresh status:', e)
    }
  }

  function startPolling(intervalMs: number = 2000) {
    if (pollInterval) return

    pollInterval = setInterval(async () => {
      await refresh()
      if (status.value.status !== 'running') {
        stopPolling()
      }
    }, intervalMs)
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  async function startGeneration(): Promise<{ success: boolean; message: string }> {
    try {
      const result = await api.startGeneration()
      startPolling()
      return { success: true, message: result.message }
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to start generation'
      return { success: false, message }
    }
  }

  return {
    status,
    generating,
    isIdle,
    isComplete,
    isError,
    refresh,
    startPolling,
    stopPolling,
    startGeneration,
  }
})
