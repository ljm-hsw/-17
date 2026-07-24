<template>
  <view class="ai-thinking" aria-label="正在回复">
    <view v-for="index in 3" :key="index" class="ai-thinking__dot" />
    <text>正在回复</text>
  </view>
</template>

<style scoped>
.ai-thinking {
  display: flex;
  min-height: 38rpx;
  align-items: center;
  gap: 8rpx;
  color: #74817c;
  font-size: 23rpx;
}

.ai-thinking__dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  animation: ai-thinking-bounce 1.1s ease-in-out infinite;
  background: #64a38f;
}

.ai-thinking__dot:nth-child(2) {
  animation-delay: 0.15s;
}

.ai-thinking__dot:nth-child(3) {
  animation-delay: 0.3s;
}

.ai-thinking text {
  margin-left: 4rpx;
}

@keyframes ai-thinking-bounce {
  0%,
  60%,
  100% {
    opacity: 0.4;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-6rpx);
  }
}
</style>
