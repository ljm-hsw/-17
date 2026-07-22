<script setup lang="ts">
import type { AiGenerationResultData } from '../../types/ai-generation'

defineProps<{ result: AiGenerationResultData; routeNames: readonly string[] }>()
const emit = defineEmits<{ copy: [content: string] }>()
</script>

<template>
  <view class="result-content">
    <text class="result-content__title">{{ result.title }}</text>
    <view class="result-content__route">
      <text class="result-content__label">本次演示路线</text>
      <text>{{ routeNames.join(' → ') }}</text>
    </view>
    <view class="result-content__story">
      <text class="result-content__section-title">旅程故事</text>
      <text class="result-content__body">{{ result.story }}</text>
    </view>
    <view class="result-content__copy-card">
      <view><text class="result-content__section-title">朋友圈文案</text><text class="result-content__body">{{ result.momentsCopy }}</text></view>
      <button @tap="emit('copy', result.momentsCopy)">复制</button>
    </view>
    <view class="result-content__copy-card">
      <view><text class="result-content__section-title">小红书标题模板</text><text class="result-content__body">{{ result.redBookCopy }}</text></view>
      <button @tap="emit('copy', result.redBookCopy)">复制</button>
    </view>
  </view>
</template>

<style scoped>
.result-content { display: flex; gap: 24rpx; flex-direction: column; }
.result-content__title { color: #254a3e; font-family: serif; font-size: 40rpx; font-weight: 800; line-height: 58rpx; }
.result-content__route, .result-content__story, .result-content__copy-card { padding: 25rpx 27rpx; border-radius: 25rpx; background: #fff; box-shadow: 0 8rpx 24rpx rgba(91, 76, 61, .07); }
.result-content__route text { display: block; color: #49635a; font-size: 24rpx; line-height: 38rpx; }
.result-content__route .result-content__label { margin-bottom: 8rpx; color: #2f8d72; font-size: 22rpx; font-weight: 800; }
.result-content__section-title, .result-content__body { display: block; }
.result-content__section-title { color: #387963; font-size: 25rpx; font-weight: 800; }
.result-content__body { margin-top: 11rpx; color: #5f625e; font-size: 25rpx; line-height: 43rpx; }
.result-content__copy-card { display: flex; align-items: flex-start; gap: 20rpx; }
.result-content__copy-card view { min-width: 0; flex: 1; }
.result-content__copy-card button { width: 96rpx; height: 56rpx; flex: none; margin: 0; padding: 0; border: 2rpx solid #83bbaa; border-radius: 28rpx; background: #f2faf7; color: #357b66; font-size: 22rpx; line-height: 54rpx; }
.result-content__copy-card button::after { border: 0; }
</style>
