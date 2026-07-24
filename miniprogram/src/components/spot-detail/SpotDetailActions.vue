<script setup lang="ts">
defineProps<{
  isInRoute: boolean
}>()

const emit = defineEmits<{
  toggleRoute: []
  openGuide: []
}>()
</script>

<template>
  <view class="spot-detail-actions">
    <view class="spot-detail-actions__inner">
      <view
        class="spot-detail-actions__button spot-detail-actions__button--route"
        :class="{ 'spot-detail-actions__button--joined': isInRoute }"
        hover-class="spot-detail-actions__button--pressed"
        @tap="emit('toggleRoute')"
      >
        <text>{{ isInRoute ? '移出路线' : '加入路线' }}</text>
      </view>
      <view
        class="spot-detail-actions__button spot-detail-actions__button--guide"
        hover-class="spot-detail-actions__button--pressed"
        @tap="emit('openGuide')"
      >
        <text>前往导览</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.spot-detail-actions {
  position: fixed;
  z-index: 30;
  right: 0;
  bottom: 0;
  left: 0;
  box-sizing: border-box;
  padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid rgba(126, 110, 94, 0.1);
  background: rgba(251, 246, 240, 0.97);
  box-shadow: 0 -8rpx 24rpx rgba(110, 92, 75, 0.08);
}

.spot-detail-actions__inner {
  display: flex;
  gap: 24rpx;
}

.spot-detail-actions__button {
  display: flex;
  height: 102rpx;
  flex: 1;
  align-items: center;
  justify-content: center;
  border-radius: 52rpx;
  color: #ffffff;
  font-size: 31rpx;
  font-weight: 700;
}

.spot-detail-actions__button--route {
  background: #e99342;
  box-shadow: 0 7rpx 18rpx rgba(233, 147, 66, 0.2);
}

.spot-detail-actions__button--joined {
  background: #d77f35;
}

.spot-detail-actions__button--guide {
  background: #3daf91;
  box-shadow: 0 7rpx 18rpx rgba(61, 175, 145, 0.2);
}

.spot-detail-actions__button--pressed {
  opacity: 0.78;
}
</style>
