<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  suggestedStayText: string
  recommendedTimes: readonly string[]
  isCheckedIn: boolean
}>()

const emit = defineEmits<{
  requestLocation: []
}>()

const recommendedTimesLabel = computed(() => props.recommendedTimes.join('、'))
</script>

<template>
  <view class="spot-visit-info">
    <view v-if="suggestedStayText.trim()" class="spot-visit-info__row">
      <text class="spot-visit-info__label">推荐游览时长</text>
      <text class="spot-visit-info__value">{{ suggestedStayText }}</text>
    </view>
    <view v-if="recommendedTimesLabel" class="spot-visit-info__row">
      <text class="spot-visit-info__label">适合的时间段</text>
      <text class="spot-visit-info__value">{{ recommendedTimesLabel }}</text>
    </view>
    <view class="spot-visit-info__row">
      <text class="spot-visit-info__label">打卡状态</text>
      <text
        class="spot-visit-info__value"
        :class="{ 'spot-visit-info__value--checked': isCheckedIn }"
      >
        {{ isCheckedIn ? '已打卡' : '未打卡' }}
      </text>
    </view>
    <view class="spot-visit-info__row">
      <text class="spot-visit-info__label">距离信息</text>
      <view class="spot-visit-info__distance" @tap="emit('requestLocation')">
        <text>开启定位后查看距离</text>
        <text class="spot-visit-info__arrow">›</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.spot-visit-info {
  margin: 34rpx 36rpx 0;
  padding: 16rpx 28rpx;
  border-radius: 24rpx;
  background: #fffdf9;
  box-shadow: 0 5rpx 18rpx rgba(135, 118, 101, 0.06);
}

.spot-visit-info__row {
  display: flex;
  min-height: 72rpx;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
  border-bottom: 1rpx solid #eee6de;
  color: #57524d;
  font-size: 27rpx;
  line-height: 40rpx;
}

.spot-visit-info__row:last-child {
  border-bottom: 0;
}

.spot-visit-info__label {
  flex: none;
}

.spot-visit-info__value,
.spot-visit-info__distance {
  min-width: 0;
  text-align: right;
}

.spot-visit-info__value--checked {
  color: #3c927d;
  font-weight: 700;
}

.spot-visit-info__distance {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  color: #2c9182;
  font-weight: 700;
}

.spot-visit-info__arrow {
  margin-left: 7rpx;
  font-size: 36rpx;
  font-weight: 400;
}
</style>
