<script setup lang="ts">
const systemInfo = uni.getSystemInfoSync()
const statusBarHeight = systemInfo.statusBarHeight ?? 20
let navigationBarHeight = 44

try {
  const menuButton = uni.getMenuButtonBoundingClientRect()
  const gap = menuButton.top - statusBarHeight
  if (menuButton.height > 0 && gap >= 0) navigationBarHeight = menuButton.height + gap * 2
} catch {
  navigationBarHeight = 44
}

defineEmits<{ back: [] }>()
</script>

<template>
  <view class="materials-header" :style="{ paddingTop: `${statusBarHeight}px` }">
    <view class="materials-header__bar" :style="{ height: `${navigationBarHeight}px` }">
      <view class="materials-header__back" hover-class="materials-header__pressed" @tap="$emit('back')">
        <image src="/static/guide/icon-back.svg" alt="返回" mode="aspectFit" />
      </view>
      <text class="materials-header__title">旅程影像</text>
    </view>
  </view>
</template>

<style scoped>
.materials-header { flex: none; background: #fbf7f1; }
.materials-header__bar { position: relative; display: flex; min-height: 88rpx; align-items: center; justify-content: center; }
.materials-header__back { position: absolute; left: 18rpx; display: flex; width: 70rpx; height: 70rpx; align-items: center; justify-content: center; }
.materials-header__back image { width: 54rpx; height: 54rpx; }
.materials-header__title { color: #263c35; font-size: 40rpx; font-weight: 700; }
.materials-header__pressed { opacity: 0.65; }
</style>
