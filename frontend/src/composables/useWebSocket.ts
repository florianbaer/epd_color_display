/**
 * Composable for WebSocket connection with auto-reconnect.
 */

import { ref, onMounted, onUnmounted } from 'vue'
import type { WebSocketMessage } from '../types'

export function useWebSocket(onMessage?: (message: WebSocketMessage) => void) {
  const connected = ref(false)
  let ws: WebSocket | null = null
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null
  let isUnmounting = false

  function getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}/api/v1/ws`
  }

  function connect() {
    if (isUnmounting) return

    try {
      ws = new WebSocket(getWebSocketUrl())

      ws.onopen = () => {
        connected.value = true
        console.log('WebSocket connected')
      }

      ws.onclose = () => {
        connected.value = false
        console.log('WebSocket disconnected')

        // Auto-reconnect after 3 seconds
        if (!isUnmounting) {
          reconnectTimeout = setTimeout(connect, 3000)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage
          if (onMessage) {
            onMessage(message)
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }
    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      // Try to reconnect
      if (!isUnmounting) {
        reconnectTimeout = setTimeout(connect, 3000)
      }
    }
  }

  function disconnect() {
    isUnmounting = true

    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }

    if (ws) {
      ws.close()
      ws = null
    }
  }

  function send(data: unknown) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    send,
    disconnect,
  }
}
