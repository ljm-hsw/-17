<script setup lang="ts">
import type { GuideRouteSummary } from '../../types/guide'

defineProps<{
  route: GuideRouteSummary
}>()

defineEmits<{
  viewRoute: []
}>()
</script>

<template>
  <view class="route-card">
    <view class="route-card__heading">
      <text class="route-card__title">{{ route.name }}</text>
      <text class="route-card__duration">（{{ route.durationLabel }}）</text>
    </view>
    <view class="route-card__bottom">
      <view class="route-card__progress">
        <text class="route-card__label">已完成</text>
        <text class="route-card__done">{{ route.completedSpotCount }}</text>
        <text class="route-card__slash">/</text>
        <text class="route-card__total">{{ route.totalSpotCount }}</text>
        <text class="route-card__label">个点位</text>
      </view>
      <view
        class="route-card__button"
        hover-class="route-card__button--pressed"
        @tap="$emit('viewRoute')"
      >
        <text>查看路线</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.route-card {
  box-sizing: border-box;
  width: calc(100% - 56rpx);
  min-height: 218rpx;
  margin: 0 auto;
  padding: 30rpx 32rpx;
  border-radius: 34rpx;
  background: #fffefb;
  box-shadow: 0 10rpx 20rpx rgba(115, 97, 77, 0.13);
}

.route-card__heading,
.route-card__bottom,
.route-card__progress {
  display: flex;
  align-items: center;
}

.route-card__title {
  color: #171816;
  font-size: 36rpx;
  font-weight: 700;
}

.route-card__duration {
  margin-left: 18rpx;
  color: #77746e;
  font-size: 26rpx;
  font-weight: 500;
}

.route-card__bottom {
  justify-content: space-between;
  margin-top: 24rpx;
}

.route-card__progress {
  gap: 9rpx;
}

.route-card__label,
.route-card__slash {
  color: #77746e;
  font-size: 28rpx;
  font-weight: 500;
}

.route-card__done,
.route-card__total {
  font-size: 38rpx;
  font-weight: 700;
}

.route-card__done {
  color: #e18d58;
}

.route-card__total {
  color: #278c79;
}

.route-card__button {
  display: flex;
  width: 176rpx;
  height: 98rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50rpx;
  background: #e8f4f0;
  color: #354d46;
  font-size: 28rpx;
  font-weight: 700;
}

.route-card__button--pressed {
  opacity: 0.72;
}
</style>
