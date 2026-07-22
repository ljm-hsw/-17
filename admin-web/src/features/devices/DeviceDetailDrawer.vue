<script setup lang="ts">
import { ElDrawer } from 'element-plus'

import type { CheckinEvent } from '../../types/dashboard'
import type { Device } from '../../types/device'

defineProps<{ modelValue: boolean; device: Device | null; events: CheckinEvent[]; spotName: string }>()
defineEmits<{ 'update:modelValue': [value: boolean]; rotate: [] }>()
const formatTime = (value: string | null) => value ? new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) : '从未上报'
</script>

<template>
  <ElDrawer :model-value="modelValue" title="设备详情" size="min(600px, 94vw)" @close="$emit('update:modelValue', false)">
    <template v-if="device">
      <section class="device-identity"><span :class="device.status">{{ device.status === 'active' ? '已启用' : '已停用' }}</span><h2>{{ device.device_id }}</h2><p>{{ device.device_type.toUpperCase() }} · {{ spotName }}</p></section>
      <dl><div><dt>密钥指纹</dt><dd><code>{{ device.secret_fingerprint || '未生成' }}</code></dd></div><div><dt>固件版本</dt><dd>{{ device.firmware_version || '未知' }}</dd></div><div><dt>最后心跳</dt><dd>{{ formatTime(device.last_seen_at) }}</dd></div><div><dt>最后错误</dt><dd>{{ device.last_error_code || '无' }}</dd></div></dl>
      <button v-if="device.status === 'active'" type="button" class="rotate" @click="$emit('rotate')">轮换设备密钥</button>
      <section class="events"><h3>最近打卡事件</h3><p v-if="events.length === 0">暂无设备事件</p><ul v-else><li v-for="event in events" :key="event.id"><span>{{ event.event_id }}</span><em>{{ event.status }}</em><time>{{ formatTime(event.received_at) }}</time></li></ul></section>
    </template>
  </ElDrawer>
</template>

<style scoped>
.device-identity h2, .device-identity p { margin: 0; }
.device-identity h2 { margin: 10px 0 4px; }
.device-identity p, .events > p { color: var(--tw-color-muted); }
.device-identity > span { padding: 4px 8px; border-radius: 999px; background: var(--tw-color-primary-soft); color: var(--tw-color-primary); font-size: 10px; }
.device-identity > span.disabled { background: #fff0ed; color: var(--tw-color-danger); }
dl { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 22px 0; }
dl div { padding: 13px; border-radius: var(--tw-radius-sm); background: #f6f8f6; }
dt { color: var(--tw-color-muted); font-size: 10px; }
dd { margin: 5px 0 0; font-size: 13px; }
.rotate { min-height: 42px; padding: 0 14px; border: 1px solid #edc2b8; border-radius: var(--tw-radius-sm); background: #fff; color: var(--tw-color-danger); font-weight: 700; }
.events { margin-top: 24px; padding-top: 18px; border-top: 1px solid var(--tw-color-border); }
.events h3 { font-size: 15px; }
ul { margin: 0; padding: 0; list-style: none; }
li { min-height: 44px; display: grid; grid-template-columns: 1fr auto auto; align-items: center; gap: 10px; border-bottom: 1px solid #eef2ef; font-size: 11px; }
li em, li time { color: var(--tw-color-muted); font-style: normal; }
</style>
