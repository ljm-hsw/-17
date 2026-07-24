<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getBackendHealth } from '../services/api'

const status = ref<'loading' | 'ok' | 'error'>('loading')

onMounted(async () => {
  try {
    status.value = await getBackendHealth()
  } catch {
    status.value = 'error'
  }
})
</script>

<template>
  <main class="dashboard">
    <section class="hero">
      <p class="eyebrow">TRAVELWEAVE · JIANG'AN</p>
      <h1>游迹织梦管理中心</h1>
      <p class="description">点位、设备、卡片与游览服务的统一运营入口</p>
      <p class="status" data-test="backend-status">
        <span class="status-dot" :class="`status-dot--${status}`" />
        后端状态：{{ status === 'ok' ? '正常' : status === 'error' ? '不可用' : '检查中' }}
      </p>
    </section>
  </main>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
  background:
    radial-gradient(circle at 15% 20%, rgb(207 231 219 / 70%), transparent 35%),
    linear-gradient(145deg, #f7f2e9 0%, #edf4ef 100%);
  color: #193c32;
}

.hero {
  width: min(760px, 100%);
  padding: 64px;
  border: 1px solid rgb(43 76 63 / 14%);
  border-radius: 28px;
  background: rgb(255 255 255 / 76%);
  box-shadow: 0 24px 80px rgb(35 65 53 / 12%);
  backdrop-filter: blur(18px);
}

.eyebrow {
  margin: 0 0 16px;
  color: #a36b3f;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.16em;
}

h1 {
  margin: 0;
  font-size: clamp(36px, 6vw, 62px);
  line-height: 1.1;
}

.description {
  margin: 24px 0 48px;
  color: #64756e;
  font-size: 18px;
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  padding: 10px 16px;
  border-radius: 999px;
  background: #edf4ef;
  font-size: 14px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d5a445;
}

.status-dot--ok {
  background: #3b8b6d;
}

.status-dot--error {
  background: #c55b4d;
}

@media (max-width: 640px) {
  .hero {
    padding: 40px 28px;
  }
}
</style>
