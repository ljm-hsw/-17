<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getBackendHealth } from '../../services/api'

const backendStatus = ref('检查中')

onMounted(async () => {
  try {
    backendStatus.value = (await getBackendHealth()) === 'ok' ? '正常' : '不可用'
  } catch {
    backendStatus.value = '不可用'
  }
})
</script>

<template>
  <view class="page">
    <view class="brand">
      <text class="eyebrow">TRAVELWEAVE · JIANG'AN</text>
      <text class="title">游迹织梦</text>
      <text class="subtitle">四川大学江安校区</text>
    </view>
    <view class="status-card">
      <text class="status-label">开发环境后端</text>
      <text class="status-value">{{ backendStatus }}</text>
    </view>
  </view>
</template>

<style scoped>
.page {
  min-height: 100vh;
  padding: 112rpx 48rpx;
  background: linear-gradient(155deg, #f7f0e5 0%, #eaf2ec 100%);
  color: #24483c;
}

.brand {
  display: flex;
  flex-direction: column;
}

.eyebrow {
  color: #a36b3f;
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 4rpx;
}

.title {
  margin-top: 28rpx;
  font-size: 72rpx;
  font-weight: 700;
  line-height: 1.15;
}

.subtitle {
  margin-top: 20rpx;
  color: #64756e;
  font-size: 30rpx;
}

.status-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 96rpx;
  padding: 32rpx 36rpx;
  border: 1rpx solid rgb(36 72 60 / 12%);
  border-radius: 28rpx;
  background: rgb(255 255 255 / 72%);
  box-shadow: 0 24rpx 80rpx rgb(36 72 60 / 10%);
}

.status-label {
  color: #64756e;
  font-size: 26rpx;
}

.status-value {
  color: #3b8b6d;
  font-size: 28rpx;
  font-weight: 700;
}
</style>
