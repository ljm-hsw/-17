<script setup lang="ts">
import type { ProfileStats } from '../../types/profile'

defineProps<{
  stats: ProfileStats
}>()
</script>

<template>
  <view class="profile-stats">
    <text class="profile-section-title">我的数据</text>
    <view class="profile-stats__grid">
      <view class="profile-stats__item">
        <text class="profile-stats__label">已打卡</text>
        <text class="profile-stats__value">{{ stats.checkedCount }}</text>
      </view>
      <view class="profile-stats__item">
        <text class="profile-stats__label">总点位</text>
        <text class="profile-stats__value">{{ stats.totalCount }}</text>
      </view>
      <view class="profile-stats__item">
        <text class="profile-stats__label">完成度</text>
        <text class="profile-stats__value">{{ stats.completionRate }}%</text>
      </view>
    </view>
    <text class="profile-stats__hint">还有{{ stats.uncheckedCount }}个点位待探索</text>
  </view>
</template>

<style scoped>
.profile-section-title {
  display: block;
  color: #2d2b28;
  font-size: 32rpx;
  font-weight: 700;
  line-height: 48rpx;
}

.profile-stats__grid {
  display: flex;
  gap: 14rpx;
  margin-top: 12rpx;
}

.profile-stats__item {
  display: flex;
  min-width: 0;
  min-height: 136rpx;
  flex: 1;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: 14rpx 8rpx;
  border-radius: 24rpx;
  background: #fffdfc;
  flex-direction: column;
}

.profile-stats__label {
  color: #837b74;
  font-size: 24rpx;
  line-height: 36rpx;
  white-space: nowrap;
}

.profile-stats__value {
  margin-top: 4rpx;
  color: #479e84;
  font-size: 44rpx;
  font-weight: 700;
  line-height: 58rpx;
  white-space: nowrap;
}

.profile-stats__hint {
  display: block;
  margin-top: 14rpx;
  color: #8b847c;
  font-size: 23rpx;
  line-height: 34rpx;
  text-align: center;
}
</style>
