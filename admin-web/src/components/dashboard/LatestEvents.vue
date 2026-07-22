<script setup lang="ts">
import PageState from '../feedback/PageState.vue'
import type { CheckinEvent } from '../../types/dashboard'

defineProps<{ items: CheckinEvent[]; loading: boolean; error: string }>()
defineEmits<{ retry: [] }>()

const time = (value: string) => new Intl.DateTimeFormat('zh-CN', { hour: '2-digit', minute: '2-digit' }).format(new Date(value))
</script>

<template>
  <section class="panel" data-test="latest-events">
    <header><div><h2>实时打卡</h2><p>每 5 秒自动刷新最近事件</p></div><span class="live"><i />LIVE</span></header>
    <PageState v-if="error" status="error" :description="error" @retry="$emit('retry')" />
    <PageState v-else-if="loading && items.length === 0" status="loading" title="正在读取打卡事件" />
    <PageState v-else-if="items.length === 0" status="empty" title="当前时段暂无打卡" />
    <ul v-else>
      <li v-for="item in items" :key="item.id">
        <span class="event-type">{{ item.checkin_type.toUpperCase() }}</span>
        <span><strong>{{ item.event_id }}</strong><small>设备 {{ item.device_id.slice(0, 8) }}</small></span>
        <time :datetime="item.received_at">{{ time(item.received_at) }}</time>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.panel { height: 100%; padding: 22px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; box-shadow: var(--tw-shadow-card); }
header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 14px; }
h2, p { margin: 0; }
h2 { font-size: 16px; }
p { margin-top: 4px; color: var(--tw-color-muted); font-size: 11px; }
.live { display: flex; align-items: center; gap: 5px; color: var(--tw-color-primary); font-size: 10px; font-weight: 800; }
.live i { width: 7px; height: 7px; border-radius: 50%; background: #44aa81; box-shadow: 0 0 0 4px #e5f5ee; }
ul { margin: 0; padding: 0; list-style: none; }
li { min-height: 48px; display: flex; align-items: center; gap: 11px; border-bottom: 1px solid #eef2ef; }
li:last-child { border: 0; }
.event-type { min-width: 45px; padding: 4px 6px; border-radius: 7px; background: var(--tw-color-primary-soft); color: var(--tw-color-primary); font-size: 9px; font-weight: 800; text-align: center; }
li > span:nth-child(2) { min-width: 0; display: grid; flex: 1; gap: 2px; }
strong { overflow: hidden; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
small, time { color: var(--tw-color-muted); font-size: 10px; }
:deep(.page-state) { min-height: 210px; }
</style>
