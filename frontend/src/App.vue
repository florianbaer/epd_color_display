<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { TabType } from './types'
import { useImageStore } from './stores/imageStore'
import { websocketService } from './services/websocket'

import AppHeader from './components/layout/AppHeader.vue'
import TabNavigation from './components/layout/TabNavigation.vue'
import EditorView from './views/EditorView.vue'
import GalleryView from './views/GalleryView.vue'

const imageStore = useImageStore()

const activeTab = ref<TabType>('editor')

function handleTabChange(tab: TabType) {
  activeTab.value = tab
  if (tab === 'gallery') {
    imageStore.loadFeed()
  }
}

onMounted(() => {
  websocketService.connect()
})

onUnmounted(() => {
  websocketService.disconnect()
})
</script>

<template>
  <div class="min-h-screen bg-gradient-primary p-5 flex items-start justify-center">
    <div class="w-full max-w-4xl bg-white rounded-xl shadow-2xl flex flex-col" style="max-height: calc(100vh - 2.5rem);">
      <AppHeader />
      <TabNavigation
        :active-tab="activeTab"
        @update:active-tab="handleTabChange"
      />

      <EditorView v-if="activeTab === 'editor'" class="overflow-y-auto flex-1 min-h-0" />
      <GalleryView v-else-if="activeTab === 'gallery'" class="flex-1 min-h-0" />
    </div>
  </div>
</template>
