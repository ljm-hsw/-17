<script setup lang="ts">
import { GridComponent, TooltipComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'
import { init, type ECharts } from 'echarts/core'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { CheckinTrendItem } from '../../types/dashboard'

const props = defineProps<{ items: CheckinTrendItem[] }>()
const element = ref<HTMLElement | null>(null)
let chart: ECharts | null = null

use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])

function render() {
  if (!chart) return
  chart.setOption({
    animationDuration: 300,
    grid: { left: 42, right: 18, top: 20, bottom: 34 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.items.map((item) => item.date.slice(5)),
      axisLine: { lineStyle: { color: '#dfe7e2' } },
      axisLabel: { color: '#60736c' },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#eef2ef' } },
      axisLabel: { color: '#60736c' },
    },
    series: [
      {
        name: '打卡次数',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        data: props.items.map((item) => item.count),
        lineStyle: { width: 3, color: '#2f8066' },
        itemStyle: { color: '#2f8066' },
        areaStyle: { color: 'rgba(47,128,102,.12)' },
      },
    ],
  })
}

function resize() {
  chart?.resize()
}

onMounted(async () => {
  await nextTick()
  if (!element.value) return
  chart = init(element.value)
  render()
  window.addEventListener('resize', resize)
})

watch(() => props.items, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
</script>

<template>
  <div ref="element" class="trend-chart" role="img" aria-label="所选时间范围内每日打卡趋势图" />
  <table class="visually-hidden">
    <caption>每日有效打卡次数</caption>
    <thead><tr><th>日期</th><th>打卡次数</th></tr></thead>
    <tbody><tr v-for="item in items" :key="item.date"><td>{{ item.date }}</td><td>{{ item.count }}</td></tr></tbody>
  </table>
</template>

<style scoped>
.trend-chart {
  width: 100%;
  min-height: 260px;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
