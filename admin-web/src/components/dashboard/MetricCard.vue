<script setup lang="ts">
import type { Component } from 'vue'

withDefaults(
  defineProps<{
    label: string
    value?: number
    note: string
    icon: Component
    loading?: boolean
    error?: string
    testId: string
  }>(),
  { value: undefined, loading: false, error: '' },
)
</script>

<template>
  <article class="metric-card" :data-test="testId">
    <div class="metric-icon"><component :is="icon" aria-hidden="true" /></div>
    <div>
      <p>{{ label }}</p>
      <strong v-if="error" class="metric-error">—</strong>
      <strong v-else>{{ loading && value === undefined ? '···' : (value ?? 0).toLocaleString() }}</strong>
      <small>{{ error || note }}</small>
    </div>
  </article>
</template>

<style scoped>
.metric-card {
  min-height: 124px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border: 1px solid var(--tw-color-border);
  border-radius: var(--tw-radius-md);
  background: var(--tw-color-surface);
  box-shadow: var(--tw-shadow-card);
}

.metric-icon {
  width: 42px;
  height: 42px;
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 12px;
  background: var(--tw-color-primary-soft);
  color: var(--tw-color-primary);
}

.metric-icon :deep(svg) {
  width: 21px;
}

p,
small {
  margin: 0;
  color: var(--tw-color-muted);
}

p {
  font-size: 13px;
}

strong {
  display: block;
  margin: 5px 0 2px;
  color: var(--tw-color-text);
  font-size: 28px;
  line-height: 1.1;
}

small {
  font-size: 11px;
}

.metric-error {
  color: var(--tw-color-danger);
}
</style>
