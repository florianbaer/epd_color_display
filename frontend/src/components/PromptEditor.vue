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
  if (charCount.value >= maxLen) return 'error'
  if (charCount.value >= maxLen * 0.9) return 'warning'
  return ''
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
      @input="handleInput"
    />
    <div class="char-count" :class="charCountClass">
      {{ charCount }} / {{ maxLen }}
    </div>
    <div class="button-group">
      <button class="btn-success" @click="handleSave">
        Save Prompt
      </button>
      <slot name="feedback" />
    </div>
  </div>
</template>
