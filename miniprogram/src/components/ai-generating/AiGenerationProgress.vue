<script setup lang="ts">
import type { AiGenerationStep } from '../../types/ai-generation'

defineProps<{ steps: readonly AiGenerationStep[]; activeIndex: number }>()
</script>

<template>
  <view class="generation-progress">
    <view
      v-for="(step, index) in steps"
      :key="step.id"
      class="generation-progress__item"
      :class="{ 'generation-progress__item--active': index <= activeIndex }"
    >
      <view class="generation-progress__dot">{{ index < activeIndex ? '✓' : index + 1 }}</view>
      <view class="generation-progress__copy">
        <text class="generation-progress__title">{{ step.title }}</text>
        <text class="generation-progress__description">{{ step.description }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.generation-progress { display: flex; padding: 30rpx; gap: 28rpx; flex-direction: column; border-radius: 30rpx; background: #fff; box-shadow: 0 10rpx 28rpx rgba(84, 71, 57, .08); }
.generation-progress__item { display: flex; align-items: center; gap: 20rpx; color: #aaa39a; }
.generation-progress__dot { display: flex; width: 54rpx; height: 54rpx; flex: none; align-items: center; justify-content: center; border-radius: 50%; background: #eee9e3; font-size: 23rpx; font-weight: 700; }
.generation-progress__copy text { display: block; }
.generation-progress__title { font-size: 27rpx; font-weight: 700; }
.generation-progress__description { margin-top: 5rpx; font-size: 22rpx; line-height: 32rpx; }
.generation-progress__item--active { color: #2e785f; }
.generation-progress__item--active .generation-progress__dot { background: #3dad8a; color: #fff; }
</style>
