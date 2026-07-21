<script setup lang="ts">
type PageStatus = 'loading' | 'empty' | 'no-results' | 'error' | 'forbidden'

withDefaults(
  defineProps<{
    status: PageStatus
    title?: string
    description?: string
    requestId?: string
  }>(),
  {
    title: '',
    description: '',
    requestId: '',
  },
)

defineEmits<{ retry: [] }>()
</script>

<template>
  <section class="page-state" :data-test="status === 'empty' ? 'empty-state' : `${status}-state`">
    <span v-if="status === 'loading'" class="spinner" aria-hidden="true" />
    <div v-else class="state-symbol" aria-hidden="true">
      {{ status === 'error' ? '!' : status === 'forbidden' ? '×' : '—' }}
    </div>
    <h3>{{ title || (status === 'loading' ? '正在加载' : '暂无数据') }}</h3>
    <p v-if="description">{{ description }}</p>
    <p v-if="requestId" class="request-id">请求编号：{{ requestId }}</p>
    <button v-if="status === 'error'" type="button" @click="$emit('retry')">重新加载</button>
  </section>
</template>

<style scoped>
.page-state {
  min-height: 260px;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 10px;
  padding: 32px;
  border: 1px dashed var(--tw-color-border);
  border-radius: var(--tw-radius-md);
  background: var(--tw-color-surface);
  text-align: center;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #dbe9e3;
  border-top-color: var(--tw-color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.state-symbol {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: var(--tw-color-primary-soft);
  color: var(--tw-color-primary);
  font-size: 22px;
  font-weight: 800;
}

h3,
p {
  margin: 0;
}

p {
  color: var(--tw-color-muted);
}

.request-id {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}

button {
  min-height: 40px;
  padding: 0 16px;
  border: 0;
  border-radius: var(--tw-radius-sm);
  background: var(--tw-color-primary);
  color: #fff;
  font-weight: 700;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
