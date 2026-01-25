<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  modelValue: string
  maxLength?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  save: [prompt: string]
}>()

const maxLen = props.maxLength ?? 1000
const localValue = ref(props.modelValue)

watch(() => props.modelValue, (newVal) => {
  localValue.value = newVal
})

const charCount = computed(() => localValue.value.length)

const charCountClass = computed(() => {
  if (charCount.value >= maxLen) return 'text-error'
  if (charCount.value >= maxLen * 0.9) return 'text-warning'
  return 'text-gray-400'
})

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  localValue.value = target.value
  emit('update:modelValue', target.value)
}

function handleSave() {
  if (localValue.value.trim()) {
    emit('save', localValue.value.trim())
  }
}
</script>

<template>
  <div>
    <textarea
      :value="localValue"
      rows="6"
      placeholder="Enter your image generation prompt..."
      :maxlength="maxLength"
      class="w-full p-3 border-2 border-gray-200 rounded-lg font-sans text-sm resize-y transition-colors duration-200 focus:outline-none focus:border-primary"
      @input="handleInput"
    />
    <div class="text-right text-xs mt-1" :class="charCountClass">
      {{ charCount }} / {{ maxLen }}
    </div>
    <div class="mt-4 flex gap-3 items-center">
      <button class="btn btn-success" @click="handleSave">
        Save Prompt
      </button>
      <slot name="feedback" />
    </div>
  </div>
</template>
