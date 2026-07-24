<script setup lang="ts">
const emit = defineEmits<{
  back: []
}>()
</script>

<template>
  <view class="spot-detail-error">
    <view class="spot-detail-error__symbol">
      <view class="spot-detail-error__pin" />
      <view class="spot-detail-error__pin-core" />
    </view>
    <text class="spot-detail-error__title">未找到该点位</text>
    <text class="spot-detail-error__description">点位参数可能缺失或已失效</text>
    <view class="spot-detail-error__button" @tap="emit('back')">
      <text>返回上一页</text>
    </view>
  </view>
</template>

<style scoped>
.spot-detail-error {
  display: flex;
  min-height: 720rpx;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  flex-direction: column;
  padding: 70rpx 48rpx;
  text-align: center;
}

.spot-detail-error__symbol {
  position: relative;
  width: 104rpx;
  height: 126rpx;
}

.spot-detail-error__pin {
  position: absolute;
  top: 0;
  left: 12rpx;
  width: 80rpx;
  height: 80rpx;
  border: 7rpx solid #78b5a4;
  border-radius: 50% 50% 50% 8rpx;
  transform: rotate(-45deg);
}

.spot-detail-error__pin-core {
  position: absolute;
  top: 28rpx;
  left: 40rpx;
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  background: #78b5a4;
}

.spot-detail-error__title {
  margin-top: 16rpx;
  color: #292724;
  font-size: 38rpx;
  font-weight: 700;
}

.spot-detail-error__description {
  margin-top: 14rpx;
  color: #827b73;
  font-size: 26rpx;
}

.spot-detail-error__button {
  display: flex;
  height: 82rpx;
  align-items: center;
  justify-content: center;
  margin-top: 38rpx;
  padding: 0 44rpx;
  border-radius: 43rpx;
  background: #3daf91;
  color: #ffffff;
  font-size: 28rpx;
  font-weight: 700;
}
</style>
