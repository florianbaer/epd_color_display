/**
 * TypeScript type definitions for the EPD Color Display frontend.
 */

export interface PromptHistoryItem {
  timestamp: string
  prompt: string
}

export interface GenerationStatus {
  status: 'idle' | 'running' | 'complete' | 'error'
  message: string
  image_path?: string
  error?: string
}

export interface SchedulerStatus {
  enabled: boolean
  schedule_time: string
  next_run: string | null
  timezone: string
}

export interface ImageInfo {
  filename: string
  path: string
  url: string
  created_at: string
  size_bytes: number
}

export interface ApiResponse<T> {
  data?: T
  error?: string
}

export interface SuccessResponse {
  success: boolean
  message: string
}

export interface WebSocketMessage {
  type: string
  prompt?: string
  data?: Record<string, unknown>
}

export type TabType = 'editor' | 'gallery'
