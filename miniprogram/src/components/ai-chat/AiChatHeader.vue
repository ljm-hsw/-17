<script setup lang="ts">
import type { AiAssistantProfile } from '../../types/ai-chat'

defineProps<{
  assistant: AiAssistantProfile
}>()

defineEmits<{
  back: []
}>()

const systemInfo = uni.getSystemInfoSync()
const statusBarHeight = systemInfo.statusBarHeight ?? 20
const windowWidth = systemInfo.windowWidth || 375
let navigationBarHeight = 48
let capsuleInset = 88

try {
  const menuButton = uni.getMenuButtonBoundingClientRect()
  const menuTopGap = menuButton.top - statusBarHeight
  if (menuButton.height > 0 && menuTopGap >= 0) {
    navigationBarHeight = menuButton.height + menuTopGap * 2
  }
  if (menuButton.left > 0) {
    capsuleInset = Math.max(88, windowWidth - menuButton.left + 8)
  }
} catch {
  navigationBarHeight = 48
  capsuleInset = 88
}

const headerStyle = {
  paddingTop: `${statusBarHeight}px`,
}

const barStyle = {
  height: `${navigationBarHeight}px`,
}

const titleStyle = {
  right: `${capsuleInset}px`,
}
</script>

<template>
  <view class="ai-chat-header" :style="headerStyle">
    <view class="ai-chat-header__bar" :style="barStyle">
      <view
        class="ai-chat-header__back"
        hover-class="ai-chat-header__pressed"
        @tap="$emit('back')"
      >
        <image src="/static/guide/icon-back.svg" alt="返回" mode="aspectFit" />
      </view>
      <view class="ai-chat-header__titles" :style="titleStyle">
        <text class="ai-chat-header__title">{{ assistant.name }}</text>
        <text class="ai-chat-header__subtitle">{{ assistant.subtitle }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.ai-chat-header {
  position: relative;
  z-index: 30;
  flex: none;
  border-bottom: 2rpx solid #eee8df;
  background: #fbf7f1;
}

.ai-chat-header__bar {
  position: relative;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding: 0 24rpx;
}

.ai-chat-header__back {
  display: flex;
  width: 64rpx;
  height: 64rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.ai-chat-header__back image {
  width: 42rpx;
  height: 42rpx;
}

.ai-chat-header__titles {
  position: absolute;
  left: 88rpx;
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
}

.ai-chat-header__title,
.ai-chat-header__subtitle {
  display: block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ai-chat-header__title {
  color: #222522;
  font-size: 38rpx;
  font-weight: 700;
  line-height: 48rpx;
}

.ai-chat-header__subtitle {
  margin-top: 2rpx;
  color: #9c9891;
  font-size: 21rpx;
  line-height: 29rpx;
}

.ai-chat-header__pressed {
  background: rgba(66, 117, 102, 0.08);
}
</style>
