<script setup lang="ts">
import type { CheckinStatsData } from '../../types/records'

defineProps<{
  stats: CheckinStatsData
}>()
</script>

<template>
  <view class="checkin-stats">
    <view class="checkin-stats__card">
      <text class="checkin-stats__label">已打卡</text>
      <text class="checkin-stats__value">{{ stats.checkedCount }} 个点位</text>
    </view>
    <view class="checkin-stats__card">
      <text class="checkin-stats__label">总点位</text>
      <text class="checkin-stats__value">{{ stats.totalCount }}</text>
    </view>
    <view class="checkin-stats__card">
      <text class="checkin-stats__label">完成度</text>
      <text class="checkin-stats__value checkin-stats__value--progress">
        {{ stats.progressPercentage }}%
      </text>
    </view>
  </view>
</template>

<style scoped>
.checkin-stats {
  display: flex;
  gap: 28rpx;
  justify-content: space-between;
}

.checkin-stats__card {
  display: flex;
  box-sizing: border-box;
  min-width: 0;
  height: 170rpx;
  flex: 1;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  border-radius: 22rpx;
  background: #fffdfc;
  box-shadow: 0 6rpx 10rpx rgba(164, 143, 126, 0.07);
  text-align: center;
}

.checkin-stats__label {
  color: #22211f;
  font-size: 29rpx;
  font-weight: 500;
  line-height: 42rpx;
}

.checkin-stats__value {
  margin-top: 4rpx;
  color: #151515;
  font-size: 43rpx;
  font-weight: 700;
  line-height: 62rpx;
  white-space: nowrap;
}

.checkin-stats__value--progress {
  color: #2f8f77;
}
</style>
