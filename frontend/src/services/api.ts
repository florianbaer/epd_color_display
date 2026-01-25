/**
 * Stateless API functions for backend communication.
 */

import type {
  PromptHistoryItem,
  GenerationStatus,
  SchedulerStatus,
  ImageInfo,
  SuccessResponse
} from '../types'

const API_BASE = '/api/v1'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
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
}

export async function getCurrentPrompt(): Promise<string> {
  const data = await fetchJson<{ prompt: string }>('/prompts/current')
  return data.prompt
}

export async function savePrompt(prompt: string): Promise<SuccessResponse> {
  return fetchJson<SuccessResponse>('/prompts/current', {
    method: 'PUT',
    body: JSON.stringify({ prompt }),
  })
}

export async function getPromptHistory(limit: number = 3): Promise<PromptHistoryItem[]> {
  const data = await fetchJson<{ prompts: PromptHistoryItem[] }>(
    `/prompts/history?limit=${limit}`
  )
  return data.prompts
}

export async function startGeneration(): Promise<{ status: string; message: string }> {
  return fetchJson('/generate', { method: 'POST' })
}

export async function getStatus(): Promise<GenerationStatus> {
  return fetchJson<GenerationStatus>('/status')
}

export async function getSchedulerStatus(): Promise<SchedulerStatus> {
  return fetchJson<SchedulerStatus>('/scheduler')
}

export async function getImages(limit: number = 50): Promise<ImageInfo[]> {
  const data = await fetchJson<{ images: ImageInfo[]; total: number }>(
    `/images?limit=${limit}`
  )
  return data.images
}

export async function displayImage(filename: string): Promise<SuccessResponse> {
  return fetchJson<SuccessResponse>(`/display/${encodeURIComponent(filename)}`, {
    method: 'POST',
  })
}
