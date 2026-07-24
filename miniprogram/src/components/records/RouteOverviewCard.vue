<script setup lang="ts">
import type { ResolvedCheckinRecord } from '../../types/records'

defineProps<{
  records: readonly ResolvedCheckinRecord[]
  totalCount: number
}>()

defineEmits<{
  viewRoute: []
}>()
</script>

<template>
  <view class="route-overview">
    <view class="route-overview__heading">
      <view class="route-overview__title-wrap">
        <text class="route-overview__title">路线概览</text>
        <text class="route-overview__progress">已完成 {{ records.length }}/{{ totalCount }}</text>
      </view>
      <view class="route-overview__link" @tap="$emit('viewRoute')">
        <text>查看完整路线</text>
        <text class="route-overview__chevron">›</text>
      </view>
    </view>

    <view class="route-overview__canvas">
      <view class="route-overview__land route-overview__land--one" />
      <view class="route-overview__land route-overview__land--two" />
      <view class="route-overview__road route-overview__road--one" />
      <view class="route-overview__road route-overview__road--two" />
      <view class="route-overview__line" />

      <view class="route-overview__stops">
        <view v-for="(entry, index) in records" :key="entry.record.id" class="route-overview__stop">
          <view class="route-overview__marker">
            <text>{{ index + 1 }}</text>
          </view>
          <text class="route-overview__name">{{ entry.spot.name }}</text>
          <text class="route-overview__time">{{ entry.record.checkedAtLabel }}</text>
        </view>
      </view>
    </view>
    <text class="route-overview__disclaimer">前端演示顺序，不代表地图服务规划路线</text>
  </view>
</template>

<style scoped>
.route-overview__heading,
.route-overview__title-wrap,
.route-overview__link,
.route-overview__stops {
  display: flex;
  align-items: center;
}

.route-overview__heading {
  justify-content: space-between;
  gap: 20rpx;
}

.route-overview__title-wrap {
  gap: 14rpx;
}

.route-overview__title {
  color: #22211f;
  font-size: 36rpx;
  font-weight: 700;
}

.route-overview__progress,
.route-overview__link {
  color: #7c7670;
  font-size: 25rpx;
}

.route-overview__link {
  flex: none;
  gap: 8rpx;
}

.route-overview__chevron {
  font-size: 34rpx;
}

.route-overview__canvas {
  position: relative;
  height: 220rpx;
  margin-top: 20rpx;
  overflow: hidden;
  border-radius: 18rpx;
  background: #dbebde;
}

.route-overview__land,
.route-overview__road,
.route-overview__line {
  position: absolute;
}

.route-overview__land {
  border-radius: 50%;
  background: rgba(177, 214, 184, 0.52);
}

.route-overview__land--one {
  width: 250rpx;
  height: 145rpx;
  top: -48rpx;
  left: -30rpx;
}

.route-overview__land--two {
  width: 280rpx;
  height: 160rpx;
  right: -70rpx;
  bottom: -58rpx;
}

.route-overview__road {
  height: 16rpx;
  border-radius: 10rpx;
  background: rgba(255, 253, 249, 0.82);
}

.route-overview__road--one {
  width: 760rpx;
  top: 62rpx;
  left: -40rpx;
  transform: rotate(-8deg);
}

.route-overview__road--two {
  width: 720rpx;
  top: 145rpx;
  left: -20rpx;
  transform: rotate(6deg);
}

.route-overview__line {
  z-index: 2;
  height: 5rpx;
  right: 88rpx;
  left: 88rpx;
  top: 73rpx;
  border-radius: 4rpx;
  background: rgba(67, 174, 145, 0.68);
}

.route-overview__stops {
  position: relative;
  z-index: 3;
  height: 100%;
  align-items: flex-start;
  justify-content: space-around;
  padding: 42rpx 18rpx 0;
}

.route-overview__stop {
  display: flex;
  min-width: 0;
  flex: 1;
  align-items: center;
  flex-direction: column;
  text-align: center;
}

.route-overview__marker {
  display: flex;
  width: 60rpx;
  height: 60rpx;
  align-items: center;
  justify-content: center;
  border: 5rpx solid rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  background: #43ae91;
  color: #ffffff;
  font-size: 27rpx;
  box-shadow: 0 5rpx 10rpx rgba(47, 143, 119, 0.2);
}

.route-overview__name {
  margin-top: 8rpx;
  color: #3f4c47;
  font-size: 23rpx;
  font-weight: 700;
  line-height: 31rpx;
}

.route-overview__time {
  color: #6f7975;
  font-size: 20rpx;
  line-height: 28rpx;
}

.route-overview__disclaimer {
  display: block;
  margin-top: 9rpx;
  color: #9a938c;
  font-size: 21rpx;
  text-align: right;
}
</style>
