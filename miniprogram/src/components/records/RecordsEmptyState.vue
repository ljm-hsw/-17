<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  actionLabel?: string
}>()

defineEmits<{
  action: []
}>()
</script>

<template>
  <view class="records-empty-state">
    <view class="records-empty-state__symbol">
      <text>✓</text>
    </view>
    <text class="records-empty-state__title">{{ title }}</text>
    <text v-if="description" class="records-empty-state__description">{{ description }}</text>
    <view v-if="actionLabel" class="records-empty-state__action" @tap="$emit('action')">
      <text>{{ actionLabel }}</text>
    </view>
  </view>
</template>

<style scoped>
.records-empty-state {
  display: flex;
  min-height: 330rpx;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 50rpx 30rpx;
  border-radius: 22rpx;
  background: #fffdfc;
  box-shadow: 0 6rpx 10rpx rgba(164, 143, 126, 0.05);
  text-align: center;
}

.records-empty-state__symbol {
  display: flex;
  width: 76rpx;
  height: 76rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #eaf6f1;
  color: #43ae91;
  font-size: 39rpx;
  font-weight: 700;
}

.records-empty-state__title {
  margin-top: 20rpx;
  color: #403d39;
  font-size: 31rpx;
  font-weight: 700;
}

.records-empty-state__description {
  margin-top: 10rpx;
  color: #8a847d;
  font-size: 25rpx;
  line-height: 38rpx;
}

.records-empty-state__action {
  display: flex;
  height: 66rpx;
  align-items: center;
  justify-content: center;
  margin-top: 26rpx;
  padding: 0 30rpx;
  border-radius: 34rpx;
  background: #43ae91;
  color: #ffffff;
  font-size: 25rpx;
  font-weight: 600;
}
</style>
