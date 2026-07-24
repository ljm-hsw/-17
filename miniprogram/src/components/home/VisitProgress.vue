<script setup lang="ts">
import { computed } from 'vue'

import type { HomeProduct, HomeProgress } from '../../types/home'

const props = defineProps<{
  progress: HomeProgress
  product: HomeProduct
}>()

defineEmits<{
  edit: []
}>()

const progressRatio = computed(() => {
  if (props.progress.totalCount <= 0) return 0
  return Math.min(1, Math.max(0, props.progress.visitedCount / props.progress.totalCount))
})

const progressPercent = computed(() => Math.round(progressRatio.value * 100))

const progressStyle = computed(() => ({
  width: `${progressRatio.value * 100}%`,
}))
</script>

<template>
  <view class="visit-progress">
    <view class="visit-progress__summary">
      <view class="visit-progress__counts">
        <text class="visit-progress__label">今日已打卡</text>
        <text class="visit-progress__current">{{ progress.visitedCount }}</text>
        <text class="visit-progress__slash">/</text>
        <text class="visit-progress__total">{{ progress.totalCount }}</text>
        <text class="visit-progress__unit">个点位</text>
      </view>
      <text class="visit-progress__percent">进度 {{ progressPercent }}%</text>
    </view>

    <view class="visit-progress__track">
      <view class="visit-progress__value" :style="progressStyle" />
    </view>

    <view class="visit-progress__product">
      <text class="visit-progress__product-text">
        {{ product.label }} {{ product.code }} {{ product.status }}
      </text>
      <view
        class="visit-progress__edit"
        hover-class="visit-progress__edit--pressed"
        @tap="$emit('edit')"
      >
        <image
          class="visit-progress__edit-icon"
          :src="product.editIcon"
          alt="编辑文创产品"
          mode="aspectFit"
        />
      </view>
    </view>
  </view>
</template>

<style scoped>
.visit-progress {
  margin: 0 44rpx;
}

.visit-progress__summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.visit-progress__counts {
  display: flex;
  align-items: baseline;
  white-space: nowrap;
}

.visit-progress__label,
.visit-progress__unit {
  color: #171816;
  font-size: 37rpx;
  font-weight: 700;
  line-height: 79rpx;
}

.visit-progress__label {
  margin-right: 18rpx;
}

.visit-progress__current,
.visit-progress__total {
  font-size: 50rpx;
  font-weight: 700;
  line-height: 88rpx;
}

.visit-progress__current {
  color: #278c79;
}

.visit-progress__slash {
  margin: 0 11rpx;
  color: #77746e;
  font-size: 44rpx;
  font-weight: 500;
}

.visit-progress__total {
  margin-right: 7rpx;
  color: #e18d58;
}

.visit-progress__percent {
  flex: none;
  color: #77746e;
  font-size: 26rpx;
  font-weight: 500;
}

.visit-progress__track {
  height: 31rpx;
  overflow: hidden;
  border-radius: 16rpx;
  background: #e8eeeb;
}

.visit-progress__value {
  height: 100%;
  border-radius: inherit;
  background: #48a995;
}

.visit-progress__product {
  display: flex;
  align-items: center;
  min-height: 72rpx;
  margin-top: 20rpx;
}

.visit-progress__product-text {
  color: #77746e;
  font-size: 29rpx;
  font-weight: 500;
  line-height: 44rpx;
}

.visit-progress__edit {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52rpx;
  height: 52rpx;
}

.visit-progress__edit--pressed {
  opacity: 0.65;
}

.visit-progress__edit-icon {
  width: 35rpx;
  height: 35rpx;
}
</style>
