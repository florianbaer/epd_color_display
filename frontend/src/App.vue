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
    imageStore.loadImages()
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
  <div class="min-h-screen bg-gradient-primary p-5">
    <div class="max-w-4xl mx-auto bg-white rounded-xl shadow-2xl overflow-hidden">
      <AppHeader />
      <TabNavigation
        :active-tab="activeTab"
        @update:active-tab="handleTabChange"
      />

      <EditorView v-if="activeTab === 'editor'" />
      <GalleryView v-else-if="activeTab === 'gallery'" />
    </div>
  </div>
</template>
