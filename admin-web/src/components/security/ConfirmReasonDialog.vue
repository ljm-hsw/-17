<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElDialog } from 'element-plus'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title: string
    description?: string
    submitting?: boolean
  }>(),
  { description: '此操作会影响现有业务数据，请确认影响并填写原因。', submitting: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [payload: { confirm: true; reason: string }]
}>()

const reason = ref('')
const errorMessage = ref('')

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      reason.value = ''
      errorMessage.value = ''
    }
  },
)

function confirm() {
  const normalized = reason.value.trim()
  if (!normalized) {
    errorMessage.value = '必须填写操作原因'
    return
  }
  errorMessage.value = ''
  emit('confirm', { confirm: true, reason: normalized })
}
</script>

<template>
  <ElDialog
    :model-value="modelValue"
    :title="title"
    width="min(480px, calc(100vw - 32px))"
    :close-on-click-modal="!submitting"
    :close-on-press-escape="!submitting"
    @close="emit('update:modelValue', false)"
  >
    <p class="risk-description">{{ description }}</p>
    <label for="risk-reason">操作原因</label>
    <textarea
      id="risk-reason"
      v-model="reason"
      data-test="risk-reason"
      rows="4"
      placeholder="请说明执行此操作的原因"
    />
    <p v-if="errorMessage" class="field-error" role="alert">{{ errorMessage }}</p>
    <template #footer>
      <button type="button" class="secondary" :disabled="submitting" @click="emit('update:modelValue', false)">
        取消
      </button>
      <button data-test="confirm-risk" type="button" class="danger" :disabled="submitting" @click="confirm">
        {{ submitting ? '正在提交…' : '确认执行' }}
      </button>
    </template>
  </ElDialog>
</template>

<style scoped>
.risk-description {
  margin: 0 0 20px;
  color: var(--tw-color-muted);
  line-height: 1.7;
}

label {
  display: block;
  margin-bottom: 8px;
  color: var(--tw-color-text);
  font-weight: 700;
}

textarea {
  width: 100%;
  padding: 12px;
  resize: vertical;
  border: 1px solid var(--tw-color-border);
  border-radius: var(--tw-radius-sm);
  color: var(--tw-color-text);
  font: inherit;
}

.field-error {
  margin: 8px 0 0;
  color: var(--tw-color-danger);
  font-size: 13px;
}

button {
  min-height: 40px;
  padding: 0 16px;
  border-radius: var(--tw-radius-sm);
  font-weight: 700;
}

.secondary {
  border: 1px solid var(--tw-color-border);
  background: #fff;
  color: var(--tw-color-text);
}

.danger {
  margin-left: 8px;
  border: 0;
  background: var(--tw-color-danger);
  color: #fff;
}
</style>
