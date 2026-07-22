<script setup lang="ts">
import type { QuickQuestion } from '../../types/ai-chat'

defineProps<{
  questions: readonly QuickQuestion[]
  disabled: boolean
}>()

defineEmits<{
  select: [question: QuickQuestion]
}>()
</script>

<template>
  <view class="quick-questions">
    <text class="quick-questions__label">你可以这样问</text>
    <view class="quick-questions__items">
      <view
        v-for="question in questions"
        :key="question.id"
        class="quick-questions__item"
        :class="{
          'quick-questions__item--disabled': disabled,
          'quick-questions__item--unavailable': question.availability === 'unavailable',
        }"
        hover-class="quick-questions__item--pressed"
        @tap="!disabled && $emit('select', question)"
      >
        <text class="quick-questions__text">{{ question.label }}</text>
        <text
          v-if="question.availability === 'unavailable'"
          class="quick-questions__badge"
        >待接入</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.quick-questions {
  margin-top: 30rpx;
}

.quick-questions__label {
  display: block;
  color: #98958e;
  font-size: 21rpx;
  line-height: 31rpx;
}

.quick-questions__items {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-top: 12rpx;
}

.quick-questions__item {
  display: inline-flex;
  min-height: 62rpx;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: 0 24rpx;
  border: 2rpx solid #e1ebe6;
  border-radius: 32rpx;
  background: #f3f7f4;
  color: #568579;
  font-size: 22rpx;
  font-weight: 600;
  line-height: 32rpx;
  white-space: nowrap;
}

.quick-questions__item--unavailable {
  border-color: #e7e1d9;
  background: #f7f3ed;
  color: #89847d;
}

.quick-questions__text {
  white-space: nowrap;
}

.quick-questions__badge {
  flex: none;
  margin-left: 10rpx;
  padding: 2rpx 10rpx;
  border-radius: 16rpx;
  background: #ece6de;
  color: #9b7460;
  font-size: 18rpx;
  font-weight: 600;
  line-height: 28rpx;
  white-space: nowrap;
}

.quick-questions__item--pressed {
  background: #e7f1ed;
}

.quick-questions__item--disabled {
  opacity: 0.48;
}
</style>
