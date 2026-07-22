<script setup lang="ts">
import { computed } from 'vue'

const emit = defineEmits<{
  back: []
}>()

const systemInfo = uni.getSystemInfoSync()
const menuButton = uni.getMenuButtonBoundingClientRect?.()
const statusBarHeight = systemInfo.statusBarHeight ?? 20
const navigationHeight = menuButton
  ? menuButton.height + Math.max(menuButton.top - statusBarHeight, 6) * 2
  : 44

const headerStyle = computed(() => ({
  paddingTop: `${statusBarHeight}px`,
  height: `${navigationHeight}px`,
}))
</script>

<template>
  <view class="recommendations-header" :style="headerStyle">
    <view class="recommendations-header__back" aria-label="返回" @tap="emit('back')">
      <image
        class="recommendations-header__back-icon"
        src="/static/guide/icon-back.svg"
        mode="aspectFit"
      />
    </view>
    <text class="recommendations-header__title">推荐点位</text>
    <view class="recommendations-header__balance" />
  </view>
</template>

<style scoped>
.recommendations-header {
  box-sizing: content-box;
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: #fbf6f0;
}

.recommendations-header__back,
.recommendations-header__balance {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 92rpx;
  height: 100%;
}

.recommendations-header__back-icon {
  width: 40rpx;
  height: 40rpx;
}

.recommendations-header__title {
  color: #183c32;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.3;
}
</style>
