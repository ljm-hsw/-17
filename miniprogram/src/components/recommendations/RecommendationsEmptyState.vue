<script setup lang="ts">
const emit = defineEmits<{
  showAll: []
}>()
</script>

<template>
  <view class="recommendations-empty">
    <view class="recommendations-empty__symbol">
      <view class="recommendations-empty__leaf recommendations-empty__leaf--left" />
      <view class="recommendations-empty__leaf recommendations-empty__leaf--right" />
    </view>
    <text class="recommendations-empty__title">当前分类暂无推荐点位</text>
    <text class="recommendations-empty__hint">换个分类，继续发现江安校园风景</text>
    <view class="recommendations-empty__button" @tap="emit('showAll')">
      <text>查看全部</text>
    </view>
  </view>
</template>

<style scoped>
.recommendations-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
  margin: 80rpx 28rpx 0;
  padding: 70rpx 30rpx;
  border-radius: 28rpx;
  background: #fffcf8;
  box-shadow: 0 12rpx 28rpx rgba(81, 66, 49, 0.07);
}

.recommendations-empty__symbol {
  position: relative;
  width: 82rpx;
  height: 70rpx;
}

.recommendations-empty__leaf {
  position: absolute;
  bottom: 8rpx;
  width: 42rpx;
  height: 58rpx;
  border-radius: 80% 10% 80% 10%;
  background: #dceee7;
}

.recommendations-empty__leaf--left {
  left: 12rpx;
  transform: rotate(-32deg);
}

.recommendations-empty__leaf--right {
  right: 6rpx;
  transform: scaleX(-1) rotate(-32deg);
  background: #bfe2d5;
}

.recommendations-empty__title {
  margin-top: 22rpx;
  color: #28483e;
  font-size: 29rpx;
  font-weight: 700;
}

.recommendations-empty__hint {
  margin-top: 12rpx;
  color: #7b8f88;
  font-size: 23rpx;
}

.recommendations-empty__button {
  margin-top: 30rpx;
  padding: 16rpx 38rpx;
  border: 1rpx solid #45b297;
  border-radius: 999rpx;
  color: #2f8f76;
  font-size: 24rpx;
  font-weight: 600;
}
</style>
