/**
 * Composable for polling generation status.
 */

import { ref, onUnmounted } from 'vue'
import type { GenerationStatus } from '../types'
import { useApi } from './useApi'

export function useStatus() {
  const status = ref<GenerationStatus>({
    status: 'idle',
    message: 'Ready',
  })

  const { getStatus } = useApi()
  let pollInterval: ReturnType<typeof setInterval> | null = null

  function startPolling(intervalMs: number = 2000) {
    stopPolling()

    pollInterval = setInterval(async () => {
      try {
        const newStatus = await getStatus()
        status.value = newStatus

        // Stop polling if generation is complete or errored
        if (newStatus.status !== 'running') {
          stopPolling()
        }
      } catch (err) {
        console.error('Status polling error:', err)
      }
    }, intervalMs)
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  async function refreshStatus() {
    try {
      status.value = await getStatus()
    } catch (err) {
      console.error('Failed to refresh status:', err)
    }
  }

  onUnmounted(() => {
    stopPolling()
  })

  return {
    status,
    startPolling,
    stopPolling,
    refreshStatus,
  }
}
