<script setup lang="ts">
import type { CheckinTab } from '../../types/records'

defineProps<{
  activeTab: CheckinTab
  checkedCount: number
  uncheckedCount: number
}>()

defineEmits<{
  select: [tab: CheckinTab]
}>()
</script>

<template>
  <view class="checkin-tabs">
    <view
      class="checkin-tabs__item"
      :class="{ 'checkin-tabs__item--active': activeTab === 'checked' }"
      @tap="$emit('select', 'checked')"
    >
      <text>已打卡（{{ checkedCount }}）</text>
    </view>
    <view
      class="checkin-tabs__item"
      :class="{ 'checkin-tabs__item--active': activeTab === 'unchecked' }"
      @tap="$emit('select', 'unchecked')"
    >
      <text>未打卡（{{ uncheckedCount }}）</text>
    </view>
  </view>
</template>

<style scoped>
.checkin-tabs {
  display: flex;
  width: 100%;
  height: 97rpx;
  overflow: hidden;
  border-radius: 50rpx;
  background: #f8f2ed;
}

.checkin-tabs__item {
  display: flex;
  min-width: 0;
  flex: 1;
  align-items: center;
  justify-content: center;
  border-radius: 50rpx;
  color: #6e6964;
  font-size: 34rpx;
  font-weight: 400;
}

.checkin-tabs__item--active {
  background: #43ae91;
  color: #ffffff;
  font-weight: 600;
}
</style>
