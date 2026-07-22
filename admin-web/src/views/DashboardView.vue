<script setup lang="ts">
import { Aim, Connection, CreditCard, UserFilled } from '@element-plus/icons-vue'
import { computed, defineAsyncComponent, ref } from 'vue'

import DeviceStatusPanel from '../components/dashboard/DeviceStatusPanel.vue'
import LatestEvents from '../components/dashboard/LatestEvents.vue'
import MetricCard from '../components/dashboard/MetricCard.vue'
import SpotRanking from '../components/dashboard/SpotRanking.vue'
import PageState from '../components/feedback/PageState.vue'
import { useDashboard } from '../features/dashboard/useDashboard'
import { useSceneStore } from '../stores/scene'

const CheckinTrendChart = defineAsyncComponent(
  () => import('../components/dashboard/CheckinTrendChart.vue'),
)

function isoDate(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const today = new Date()
const weekStart = new Date(today)
weekStart.setDate(today.getDate() - 6)

const sceneStore = useSceneStore()
const dateFrom = ref(isoDate(weekStart))
const dateTo = ref(isoDate(today))
const sceneId = computed(() => sceneStore.currentSceneId)
const currentSceneName = computed(() => sceneStore.currentScene?.name ?? '当前场景')
const dashboard = useDashboard({ sceneId, dateFrom, dateTo })

const generatedAt = computed(() => {
  if (!dashboard.summary.value?.generated_at) return '等待首次同步'
  return `更新于 ${new Intl.DateTimeFormat('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }).format(new Date(dashboard.summary.value.generated_at))}`
})
</script>

<template>
  <div class="dashboard-page">
    <header class="page-heading">
      <div>
        <p class="eyebrow">TRAVELWEAVE OPERATIONS</p>
        <h1>运营总览</h1>
        <p>{{ currentSceneName }} · {{ generatedAt }}</p>
      </div>
      <div class="date-filter" aria-label="统计日期范围">
        <label>开始日期<input v-model="dateFrom" type="date" :max="dateTo" /></label>
        <span>至</span>
        <label>结束日期<input v-model="dateTo" type="date" :min="dateFrom" /></label>
      </div>
    </header>

    <PageState
      v-if="!sceneId && sceneStore.loading"
      status="loading"
      title="正在读取校区信息"
      description="完成后将自动加载运营数据"
    />
    <PageState
      v-else-if="!sceneId"
      status="empty"
      title="尚未配置运营场景"
      description="请先在场景管理中创建江安校区。"
    />

    <template v-else>
      <section class="metric-grid" aria-label="核心运营指标">
        <MetricCard
          label="今日到访用户"
          :value="dashboard.summary.value?.today_visitors"
          note="按用户去重"
          :icon="UserFilled"
          :loading="dashboard.loading.summary"
          :error="dashboard.errors.summary"
          test-id="metric-today-visitors"
        />
        <MetricCard
          label="有效打卡"
          :value="dashboard.summary.value?.accepted_checkins"
          note="所选日期范围"
          :icon="Aim"
          :loading="dashboard.loading.summary"
          :error="dashboard.errors.summary"
          test-id="metric-accepted-checkins"
        />
        <MetricCard
          label="已绑定卡片"
          :value="dashboard.summary.value?.bound_cards"
          note="当前有效绑定"
          :icon="CreditCard"
          :loading="dashboard.loading.summary"
          :error="dashboard.errors.summary"
          test-id="metric-bound-cards"
        />
        <MetricCard
          label="在线设备"
          :value="dashboard.summary.value?.online_devices"
          :note="`共 ${dashboard.devices.value.length} 台设备`"
          :icon="Connection"
          :loading="dashboard.loading.summary"
          :error="dashboard.errors.summary"
          test-id="metric-online-devices"
        />
      </section>

      <section class="dashboard-grid dashboard-grid--primary">
        <article class="trend-panel">
          <header><div><h2>打卡趋势</h2><p>{{ dateFrom }} 至 {{ dateTo }}</p></div></header>
          <PageState
            v-if="dashboard.errors.trend"
            status="error"
            :description="dashboard.errors.trend"
            @retry="dashboard.loadSection('trend')"
          />
          <PageState
            v-else-if="dashboard.loading.trend && dashboard.trend.value.length === 0"
            status="loading"
            title="正在加载趋势"
          />
          <PageState v-else-if="dashboard.trend.value.length === 0" status="empty" title="暂无趋势数据" />
          <CheckinTrendChart v-else :items="dashboard.trend.value" />
        </article>
        <SpotRanking
          :items="dashboard.ranking.value"
          :loading="dashboard.loading.ranking"
          :error="dashboard.errors.ranking"
          @retry="dashboard.loadSection('ranking')"
        />
      </section>

      <section class="dashboard-grid dashboard-grid--secondary">
        <LatestEvents
          :items="dashboard.events.value"
          :loading="dashboard.loading.events"
          :error="dashboard.errors.events"
          @retry="dashboard.loadSection('events')"
        />
        <DeviceStatusPanel
          :items="dashboard.devices.value"
          :loading="dashboard.loading.devices"
          :error="dashboard.errors.devices"
          @retry="dashboard.loadSection('devices')"
        />
      </section>
    </template>
  </div>
</template>

<style scoped>
.dashboard-page {
  max-width: 1540px;
  margin: 0 auto;
  padding: 26px;
}

.page-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 22px;
}

.page-heading h1,
.page-heading p {
  margin: 0;
}

.page-heading h1 {
  margin: 3px 0 7px;
  font-size: clamp(24px, 3vw, 32px);
}

.page-heading > div:first-child > p:last-child {
  color: var(--tw-color-muted);
  font-size: 12px;
}

.eyebrow {
  color: var(--tw-color-accent);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.16em;
}

.date-filter {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 9px 12px;
  border: 1px solid var(--tw-color-border);
  border-radius: var(--tw-radius-sm);
  background: #fff;
}

.date-filter label {
  display: grid;
  gap: 4px;
  color: var(--tw-color-muted);
  font-size: 9px;
}

.date-filter input {
  min-height: 30px;
  border: 0;
  color: var(--tw-color-text);
  font: inherit;
  font-size: 12px;
  font-weight: 700;
}

.date-filter > span {
  padding-bottom: 8px;
  color: var(--tw-color-muted);
  font-size: 11px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 14px;
}

.dashboard-grid {
  display: grid;
  gap: 14px;
  margin-top: 14px;
}

.dashboard-grid--primary {
  grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.8fr);
}

.dashboard-grid--secondary {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.trend-panel {
  min-width: 0;
  padding: 22px;
  border: 1px solid var(--tw-color-border);
  border-radius: var(--tw-radius-md);
  background: #fff;
  box-shadow: var(--tw-shadow-card);
}

.trend-panel header {
  margin-bottom: 8px;
}

.trend-panel h2,
.trend-panel p {
  margin: 0;
}

.trend-panel h2 {
  font-size: 16px;
}

.trend-panel p {
  margin-top: 4px;
  color: var(--tw-color-muted);
  font-size: 11px;
}

.trend-panel :deep(.page-state) {
  min-height: 260px;
}

@media (max-width: 1120px) {
  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .page-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .dashboard-grid--primary,
  .dashboard-grid--secondary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .dashboard-page {
    padding: 18px 14px;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }

  .date-filter {
    width: 100%;
    align-items: stretch;
    flex-direction: column;
  }

  .date-filter > span {
    display: none;
  }
}
</style>
