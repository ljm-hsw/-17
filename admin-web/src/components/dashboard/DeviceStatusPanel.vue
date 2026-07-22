<script setup lang="ts">
import PageState from '../feedback/PageState.vue'
import type { DeviceStatus } from '../../types/dashboard'

defineProps<{ items: DeviceStatus[]; loading: boolean; error: string }>()
defineEmits<{ retry: [] }>()

function isOnline(device: DeviceStatus) {
  if (device.status !== 'active' || !device.last_seen_at) return false
  return Date.now() - new Date(device.last_seen_at).getTime() <= 120_000
}
</script>

<template>
  <section class="panel" data-test="device-status">
    <header><div><h2>设备状态</h2><p>每 10 秒检查设备心跳</p></div></header>
    <PageState v-if="error" status="error" :description="error" @retry="$emit('retry')" />
    <PageState v-else-if="loading && items.length === 0" status="loading" title="正在检查设备" />
    <PageState v-else-if="items.length === 0" status="empty" title="当前场景暂无设备" />
    <ul v-else>
      <li v-for="device in items.slice(0, 6)" :key="device.id">
        <i :class="{ online: isOnline(device) }" />
        <span><strong>{{ device.device_id }}</strong><small>{{ device.device_type.toUpperCase() }} · {{ device.firmware_version || '固件未知' }}</small></span>
        <em>{{ isOnline(device) ? '在线' : '离线' }}</em>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.panel { height: 100%; padding: 22px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; box-shadow: var(--tw-shadow-card); }
header { margin-bottom: 14px; }
h2, p { margin: 0; }
h2 { font-size: 16px; }
p { margin-top: 4px; color: var(--tw-color-muted); font-size: 11px; }
ul { margin: 0; padding: 0; list-style: none; }
li { min-height: 48px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #eef2ef; }
li:last-child { border: 0; }
li > i { width: 8px; height: 8px; border-radius: 50%; background: #b8c2be; }
li > i.online { background: #43a77f; box-shadow: 0 0 0 4px #e7f4ef; }
li span { display: grid; flex: 1; gap: 2px; }
strong { font-size: 12px; }
small { color: var(--tw-color-muted); font-size: 10px; }
em { color: var(--tw-color-muted); font-size: 10px; font-style: normal; }
:deep(.page-state) { min-height: 210px; }
</style>
