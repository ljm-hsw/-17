<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElDialog } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
  label: string
  secret: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  closed: []
}>()

const saved = ref(false)
const copied = ref(false)

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      saved.value = false
      copied.value = false
    }
  },
)

async function copySecret() {
  await navigator.clipboard.writeText(props.secret)
  copied.value = true
}

function close() {
  if (!saved.value) return
  emit('update:modelValue', false)
  emit('closed')
}
</script>

<template>
  <ElDialog
    :model-value="modelValue"
    :title="`${label}已生成`"
    width="min(520px, calc(100vw - 32px))"
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="warning" role="status">
      <strong>仅显示一次</strong>
      <span>关闭后无法再次查看，请立即复制并安全保存。</span>
    </div>
    <label>{{ label }}</label>
    <div class="secret-row">
      <code>{{ secret }}</code>
      <button data-test="copy-secret" type="button" @click="copySecret">
        {{ copied ? '已复制' : '复制' }}
      </button>
    </div>
    <label class="acknowledge">
      <input v-model="saved" data-test="secret-saved" type="checkbox" />
      我已将{{ label }}安全保存
    </label>
    <template #footer>
      <button data-test="close-secret" type="button" class="primary" :disabled="!saved" @click="close">
        完成并关闭
      </button>
    </template>
  </ElDialog>
</template>

<style scoped>
.warning {
  display: grid;
  gap: 4px;
  margin-bottom: 20px;
  padding: 14px;
  border: 1px solid #efd7c2;
  border-radius: var(--tw-radius-sm);
  background: #fff8ef;
  color: #8f4e2d;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 700;
}

.secret-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

code {
  overflow-wrap: anywhere;
  padding: 12px;
  border-radius: var(--tw-radius-sm);
  background: #eef4f1;
  color: var(--tw-color-text);
}

button {
  min-height: 40px;
  padding: 0 16px;
  border: 1px solid var(--tw-color-border);
  border-radius: var(--tw-radius-sm);
  background: #fff;
  color: var(--tw-color-primary);
  font-weight: 700;
}

.acknowledge {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  font-weight: 500;
}

.primary {
  border: 0;
  background: var(--tw-color-primary);
  color: #fff;
}

.primary:disabled {
  opacity: 0.5;
}
</style>
