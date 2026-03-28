<script setup lang="ts">
import { useImageStore } from '../../stores/imageStore'
import FeedPost from './FeedPost.vue'

const imageStore = useImageStore()

defineExpose({ refresh: () => imageStore.loadFeed() })
</script>

<template>
  <div>
    <div v-if="imageStore.loading" class="bg-gray-50 border-l-4 border-primary p-4 rounded text-sm text-gray-500">
      Loading images...
    </div>

    <div v-else-if="imageStore.feedGroups.length === 0" class="text-center py-10 text-gray-400">
      <p>No images generated yet.</p>
      <p class="mt-2">Generate an image to see it here!</p>
    </div>

    <div v-else class="flex flex-col">
      <FeedPost
        v-for="(group, index) in imageStore.feedGroups"
        :key="group.generated_at + '-' + index"
        :group="group"
      />
    </div>
  </div>
</template>
