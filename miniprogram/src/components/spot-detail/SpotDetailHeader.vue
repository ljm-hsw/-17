<script setup lang="ts">
defineProps<{
  title?: string
}>()

const emit = defineEmits<{
  back: []
}>()

const systemInfo = uni.getSystemInfoSync()
const statusBarHeight = systemInfo.statusBarHeight ?? 20
let navigationBarHeight = 44

try {
  const menuButton = uni.getMenuButtonBoundingClientRect()
  const menuTopGap = menuButton.top - statusBarHeight
  if (menuButton.height > 0 && menuTopGap >= 0) {
    navigationBarHeight = menuButton.height + menuTopGap * 2
  }
} catch {
  navigationBarHeight = 44
}

const headerStyle = {
  paddingTop: `${statusBarHeight}px`,
}

const navigationStyle = {
  height: `${navigationBarHeight}px`,
}
</script>

<template>
  <view class="spot-detail-header" :style="headerStyle">
    <view class="spot-detail-header__bar" :style="navigationStyle">
      <view
        class="spot-detail-header__back"
        hover-class="spot-detail-header__back--pressed"
        aria-label="返回"
        @tap="emit('back')"
      >
        <image src="/static/guide/icon-back.svg" alt="返回" mode="aspectFit" />
      </view>
      <text class="spot-detail-header__title">{{ title || '点位详情' }}</text>
    </view>
  </view>
</template>

<style scoped>
.spot-detail-header {
  position: relative;
  z-index: 20;
  box-sizing: border-box;
  flex: none;
  background: #fbf6f0;
}

.spot-detail-header__bar {
  position: relative;
  display: flex;
  min-height: 88rpx;
  align-items: center;
  justify-content: center;
}

.spot-detail-header__back {
  position: absolute;
  left: 18rpx;
  display: flex;
  width: 70rpx;
  height: 70rpx;
  align-items: center;
  justify-content: center;
}

.spot-detail-header__back image {
  width: 54rpx;
  height: 54rpx;
}

.spot-detail-header__back--pressed {
  opacity: 0.62;
}

.spot-detail-header__title {
  max-width: 410rpx;
  overflow: hidden;
  color: #22211f;
  font-size: 40rpx;
  font-weight: 700;
  line-height: 60rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
