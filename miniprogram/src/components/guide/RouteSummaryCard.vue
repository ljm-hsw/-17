<script setup lang="ts">
import type { GuideRouteSummary } from '../../types/guide'

defineProps<{
  route: GuideRouteSummary
  expanded: boolean
}>()

defineEmits<{
  viewRoute: []
}>()
</script>

<template>
  <view class="route-card">
    <view class="route-card__heading">
      <text class="route-card__title">{{ route.name }}</text>
    </view>
    <view class="route-card__bottom">
      <view class="route-card__stats">
        <text class="route-card__stat">
          已打卡 <text class="route-card__done">{{ route.checkedSpotCount }}</text>
          / {{ route.totalSpotCount }} 个点位
        </text>
        <text class="route-card__stat route-card__stat--route">
          当前路线共 <text class="route-card__route-count">{{ route.routeSpotCount }}</text> 个点位
        </text>
      </view>
      <view
        class="route-card__button"
        hover-class="route-card__button--pressed"
        @tap="$emit('viewRoute')"
      >
        <text>{{ expanded ? '收起路线' : '查看路线' }}</text>
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

.route-card__bottom,
.route-card__heading {
  display: flex;
  align-items: center;
}

.route-card__title {
  color: #171816;
  font-size: 36rpx;
  font-weight: 700;
}

.route-card__bottom {
  justify-content: space-between;
  margin-top: 24rpx;
}

.route-card__stats {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 10rpx;
}

.route-card__stat {
  display: block;
  color: #77746e;
  font-size: 25rpx;
  font-weight: 500;
  line-height: 36rpx;
  white-space: nowrap;
}

.route-card__stat--route {
  color: #5f756e;
}

.route-card__done,
.route-card__route-count {
  font-size: 31rpx;
  font-weight: 700;
}

.route-card__done {
  color: #e18d58;
}

.route-card__route-count {
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
