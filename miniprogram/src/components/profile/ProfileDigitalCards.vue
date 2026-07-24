<script setup lang="ts">
import type { ProfileStats } from '../../types/profile'

defineProps<{
  stats: ProfileStats
}>()

defineEmits<{
  open: []
}>()
</script>

<template>
  <view
    class="profile-digital-cards"
    hover-class="profile-digital-cards--pressed"
    @tap="$emit('open')"
  >
    <view class="profile-digital-cards__header">
      <view>
        <text class="profile-digital-cards__title">数字点位卡</text>
        <text class="profile-digital-cards__subtitle">
          已收集 {{ stats.digitalCardCount }} / {{ stats.totalCount }} 张
        </text>
      </view>
      <text class="profile-digital-cards__rate">{{ stats.completionRate }}%</text>
    </view>
    <view class="profile-digital-cards__track">
      <view
        class="profile-digital-cards__progress"
        :style="{ width: `${stats.completionRate}%` }"
      />
    </view>
    <text class="profile-digital-cards__action">查看我的打卡 ›</text>
  </view>
</template>

<style scoped>
.profile-digital-cards {
  box-sizing: border-box;
  padding: 26rpx 28rpx 24rpx;
  border: 2rpx solid #e5eee9;
  border-radius: 28rpx;
  background: linear-gradient(135deg, #f4fbf8 0%, #fffdf9 100%);
}

.profile-digital-cards--pressed {
  opacity: 0.72;
}

.profile-digital-cards__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.profile-digital-cards__title,
.profile-digital-cards__subtitle {
  display: block;
}

.profile-digital-cards__title {
  color: #2d2b28;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 44rpx;
}

.profile-digital-cards__subtitle {
  margin-top: 3rpx;
  color: #746e68;
  font-size: 24rpx;
  line-height: 36rpx;
}

.profile-digital-cards__rate {
  color: #3c9b80;
  font-size: 38rpx;
  font-weight: 700;
  line-height: 48rpx;
}

.profile-digital-cards__track {
  height: 12rpx;
  overflow: hidden;
  margin-top: 18rpx;
  border-radius: 6rpx;
  background: #dfe9e4;
}

.profile-digital-cards__progress {
  height: 100%;
  border-radius: 6rpx;
  background: #3c9b80;
}

.profile-digital-cards__action {
  display: block;
  margin-top: 15rpx;
  color: #4b927d;
  font-size: 22rpx;
  line-height: 32rpx;
  text-align: right;
}
</style>
