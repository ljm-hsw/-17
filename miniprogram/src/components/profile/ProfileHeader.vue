<script setup lang="ts">
const systemInfo = uni.getSystemInfoSync()
const statusBarHeight = systemInfo.statusBarHeight ?? 20
const windowWidth = systemInfo.windowWidth || 375
let navigationBarHeight = 44
let capsuleInset = 44

try {
  const menuButton = uni.getMenuButtonBoundingClientRect()
  const menuTopGap = menuButton.top - statusBarHeight
  if (menuButton.height > 0 && menuTopGap >= 0) {
    navigationBarHeight = menuButton.height + menuTopGap * 2
  }
  if (menuButton.left > 0) {
    capsuleInset = Math.max(44, windowWidth - menuButton.left + 8)
  }
} catch {
  navigationBarHeight = 44
  capsuleInset = 44
}

const headerStyle = {
  paddingTop: `${statusBarHeight}px`,
}

const barStyle = {
  height: `${navigationBarHeight}px`,
  paddingLeft: `${capsuleInset}px`,
  paddingRight: `${capsuleInset}px`,
}
</script>

<template>
  <view class="profile-header" :style="headerStyle">
    <view class="profile-header__bar" :style="barStyle">
      <text class="profile-header__title">我的</text>
    </view>
  </view>
</template>

<style scoped>
.profile-header {
  position: relative;
  z-index: 24;
  box-sizing: border-box;
  flex: none;
  border-bottom: 2rpx solid #eee8e1;
  background: #fffdfc;
}

.profile-header__bar {
  display: flex;
  min-height: 88rpx;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.profile-header__title {
  overflow: hidden;
  color: #22211f;
  font-size: 38rpx;
  font-weight: 700;
  line-height: 56rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
