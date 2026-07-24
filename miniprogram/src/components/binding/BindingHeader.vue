<script setup lang="ts">
const emit = defineEmits<{
  back: []
}>()

const statusBarHeight = uni.getSystemInfoSync().statusBarHeight ?? 20
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
  <view class="binding-header" :style="headerStyle">
    <view class="binding-header__bar" :style="navigationStyle">
      <view
        class="binding-header__back"
        hover-class="binding-header__back--pressed"
        aria-label="返回"
        @tap="emit('back')"
      >
        <text>‹</text>
      </view>
      <text class="binding-header__title">系统绑卡</text>
    </view>
  </view>
</template>

<style scoped>
.binding-header {
  position: relative;
  z-index: 10;
  flex: none;
  background: #faf5f0;
}

.binding-header__bar {
  position: relative;
  display: flex;
  min-height: 88rpx;
  align-items: center;
  justify-content: center;
}

.binding-header__back {
  position: absolute;
  left: 24rpx;
  display: flex;
  width: 72rpx;
  height: 72rpx;
  align-items: center;
  justify-content: center;
  color: #333333;
  font-size: 56rpx;
  font-weight: 400;
  line-height: 72rpx;
}

.binding-header__back--pressed {
  opacity: 0.58;
}

.binding-header__title {
  color: #333333;
  font-size: 35rpx;
  font-weight: 500;
  line-height: 52rpx;
}
</style>
