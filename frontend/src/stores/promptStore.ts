import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PromptHistoryItem } from '../types'
import * as api from '../services/api'

export const usePromptStore = defineStore('prompt', () => {
  const prompt = ref('')
  const history = ref<PromptHistoryItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadCurrent() {
    loading.value = true
    error.value = null
    try {
      prompt.value = await api.getCurrentPrompt()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load prompt'
    } finally {
      loading.value = false
    }
  }

  async function loadHistory(limit: number = 3) {
    try {
      history.value = await api.getPromptHistory(limit)
    } catch (e) {
      console.error('Failed to load prompt history:', e)
    }
  }

  async function save(): Promise<{ success: boolean; message: string }> {
    loading.value = true
    error.value = null
    try {
      const result = await api.savePrompt(prompt.value)
      await loadHistory()
      return result
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Failed to save prompt'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  function setPrompt(value: string) {
    prompt.value = value
  }

  return {
    prompt,
    history,
    loading,
    error,
    loadCurrent,
    loadHistory,
    save,
    setPrompt,
  }
})
