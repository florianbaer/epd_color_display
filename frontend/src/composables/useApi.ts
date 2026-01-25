/**
 * Composable for API calls to the backend.
 */

import { ref } from 'vue'
import type {
  PromptHistoryItem,
  GenerationStatus,
  SchedulerStatus,
  ImageInfo,
  SuccessResponse
} from '../types'

const API_BASE = '/api/v1'

export function useApi() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      error.value = message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getCurrentPrompt(): Promise<string> {
    const data = await fetchJson<{ prompt: string }>('/prompts/current')
    return data.prompt
  }

  async function savePrompt(prompt: string): Promise<SuccessResponse> {
    return fetchJson<SuccessResponse>('/prompts/current', {
      method: 'PUT',
      body: JSON.stringify({ prompt }),
    })
  }

  async function getPromptHistory(limit: number = 3): Promise<PromptHistoryItem[]> {
    const data = await fetchJson<{ prompts: PromptHistoryItem[] }>(
      `/prompts/history?limit=${limit}`
    )
    return data.prompts
  }

  async function startGeneration(): Promise<{ status: string; message: string }> {
    return fetchJson('/generate', { method: 'POST' })
  }

  async function getStatus(): Promise<GenerationStatus> {
    return fetchJson<GenerationStatus>('/status')
  }

  async function getSchedulerStatus(): Promise<SchedulerStatus> {
    return fetchJson<SchedulerStatus>('/scheduler')
  }

  async function getImages(limit: number = 50): Promise<ImageInfo[]> {
    const data = await fetchJson<{ images: ImageInfo[]; total: number }>(
      `/images?limit=${limit}`
    )
    return data.images
  }

  return {
    loading,
    error,
    getCurrentPrompt,
    savePrompt,
    getPromptHistory,
    startGeneration,
    getStatus,
    getSchedulerStatus,
    getImages,
  }
}
