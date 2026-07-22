<script setup lang="ts">
import PageState from '../feedback/PageState.vue'
import type { SpotRankingItem } from '../../types/dashboard'

defineProps<{ items: SpotRankingItem[]; loading: boolean; error: string }>()
defineEmits<{ retry: [] }>()
</script>

<template>
  <section class="panel" data-test="spot-ranking">
    <header><div><h2>热门点位</h2><p>按有效打卡次数排序</p></div></header>
    <PageState v-if="error" status="error" :description="error" @retry="$emit('retry')" />
    <PageState v-else-if="loading && items.length === 0" status="loading" title="正在加载排行" />
    <PageState v-else-if="items.length === 0" status="empty" title="暂无点位数据" />
    <ol v-else>
      <li v-for="(item, index) in items.slice(0, 6)" :key="item.spot_id">
        <span class="rank">{{ index + 1 }}</span>
        <span class="spot-name">{{ item.name }}</span>
        <strong>{{ item.event_count }}</strong><small>次</small>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.panel { height: 100%; padding: 22px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; box-shadow: var(--tw-shadow-card); }
header { display: flex; justify-content: space-between; margin-bottom: 16px; }
h2, p { margin: 0; }
h2 { font-size: 16px; }
p { margin-top: 4px; color: var(--tw-color-muted); font-size: 11px; }
ol { display: grid; gap: 2px; margin: 0; padding: 0; list-style: none; }
li { min-height: 40px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #eef2ef; }
li:last-child { border: 0; }
.rank { width: 24px; height: 24px; display: grid; place-items: center; border-radius: 8px; background: var(--tw-color-primary-soft); color: var(--tw-color-primary); font-size: 11px; font-weight: 800; }
.spot-name { flex: 1; font-size: 13px; }
strong { font-size: 15px; }
small { color: var(--tw-color-muted); }
:deep(.page-state) { min-height: 210px; }
</style>
