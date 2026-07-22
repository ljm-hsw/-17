<script setup lang="ts">
defineProps<{
  tip: string
}>()
</script>

<template>
  <view class="spot-checkin-tip">
    <text class="spot-checkin-tip__title">打卡贴士</text>
    <text class="spot-checkin-tip__content">{{ tip }}</text>
  </view>
</template>

<style scoped>
.spot-checkin-tip {
  margin: 34rpx 36rpx 0;
  padding: 26rpx 28rpx;
  border-radius: 24rpx;
  background: #f7eee0;
}

.spot-checkin-tip__title,
.spot-checkin-tip__content {
  display: block;
}

.spot-checkin-tip__title {
  color: #8b623b;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 44rpx;
}

.spot-checkin-tip__content {
  margin-top: 12rpx;
  color: #6a5b4e;
  font-size: 26rpx;
  line-height: 44rpx;
  overflow-wrap: anywhere;
}
</style>
