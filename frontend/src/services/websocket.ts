/**
 * WebSocket service class with auto-reconnect.
 * Updates stores on message received.
 */

import type { WebSocketMessage } from '../types'
import { useConnectionStore } from '../stores/connectionStore'
import { usePromptStore } from '../stores/promptStore'

export type MessageHandler = (message: WebSocketMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null
  private messageHandlers: MessageHandler[] = []
  private isDestroyed = false

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}/api/v1/ws`
  }

  connect() {
    if (this.isDestroyed || this.ws?.readyState === WebSocket.OPEN) return

    try {
      this.ws = new WebSocket(this.getWebSocketUrl())

      this.ws.onopen = () => {
        const connectionStore = useConnectionStore()
        connectionStore.setConnected(true)
        console.log('WebSocket connected')
      }

      this.ws.onclose = () => {
        const connectionStore = useConnectionStore()
        connectionStore.setConnected(false)
        console.log('WebSocket disconnected')

        // Auto-reconnect after 3 seconds
        if (!this.isDestroyed) {
          this.reconnectTimeout = setTimeout(() => this.connect(), 3000)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage
          this.handleMessage(message)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }
    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      // Try to reconnect
      if (!this.isDestroyed) {
        this.reconnectTimeout = setTimeout(() => this.connect(), 3000)
      }
    }
  }

  private handleMessage(message: WebSocketMessage) {
    // Handle prompt updates from other clients
    if (message.type === 'prompt_update' && message.prompt) {
      const promptStore = usePromptStore()
      promptStore.setPrompt(message.prompt)
    }

    // Call registered handlers
    this.messageHandlers.forEach(handler => handler(message))
  }

  addMessageHandler(handler: MessageHandler) {
    this.messageHandlers.push(handler)
  }

  removeMessageHandler(handler: MessageHandler) {
    const index = this.messageHandlers.indexOf(handler)
    if (index > -1) {
      this.messageHandlers.splice(index, 1)
    }
  }

  send(data: unknown) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  disconnect() {
    this.isDestroyed = true

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// Singleton instance
export const websocketService = new WebSocketService()
