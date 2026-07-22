<script setup lang="ts">
import { ref, watch } from 'vue'
import type { GuideSpot } from '../../types/guide'

const props = defineProps<{
  spot: GuideSpot
}>()

defineEmits<{
  viewSpot: [spotId: string]
}>()

const imageLoadFailed = ref(false)

watch(
  () => props.spot.id,
  () => {
    imageLoadFailed.value = false
  },
)
</script>

<template>
  <view class="spot-recommendation">
    <view class="spot-recommendation__media">
      <image
        v-if="!imageLoadFailed"
        :src="spot.coverImage"
        :alt="spot.name"
        mode="aspectFill"
        @error="imageLoadFailed = true"
      />
      <text v-else>{{ spot.name }}</text>
    </view>
    <view class="spot-recommendation__content">
      <text class="spot-recommendation__eyebrow">推荐下一站 · 演示</text>
      <text class="spot-recommendation__name">{{ spot.name }}</text>
      <text class="spot-recommendation__summary">{{ spot.summary }}</text>
      <view
        class="spot-recommendation__action"
        hover-class="spot-recommendation__action--pressed"
        @tap="$emit('viewSpot', spot.id)"
      >
        <text>查看点位</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.spot-recommendation {
  display: flex;
  box-sizing: border-box;
  width: calc(100% - 92rpx);
  min-height: 196rpx;
  gap: 22rpx;
  margin: 14rpx 0 0 92rpx;
  padding: 18rpx;
  border-radius: 28rpx;
  background: #ffffff;
  box-shadow: 0 6rpx 12rpx rgba(108, 98, 87, 0.1);
}

.spot-recommendation__media {
  display: flex;
  width: 152rpx;
  min-height: 160rpx;
  overflow: hidden;
  flex: none;
  align-items: center;
  justify-content: center;
  border-radius: 20rpx;
  background: #e4eee8;
  color: #618177;
  font-size: 21rpx;
  text-align: center;
}

.spot-recommendation__media image {
  width: 100%;
  height: 100%;
}

.spot-recommendation__content {
  position: relative;
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  padding-bottom: 56rpx;
}

.spot-recommendation__eyebrow,
.spot-recommendation__name,
.spot-recommendation__summary {
  display: block;
}

.spot-recommendation__eyebrow {
  color: #8a8c87;
  font-size: 20rpx;
  line-height: 30rpx;
}

.spot-recommendation__name {
  margin-top: 2rpx;
  color: #2b2e2b;
  font-size: 32rpx;
  font-weight: 700;
  line-height: 44rpx;
}

.spot-recommendation__summary {
  max-height: 62rpx;
  overflow: hidden;
  margin-top: 4rpx;
  color: #88857f;
  font-size: 20rpx;
  line-height: 31rpx;
}

.spot-recommendation__action {
  position: absolute;
  right: 0;
  bottom: 0;
  display: flex;
  height: 50rpx;
  align-items: center;
  justify-content: center;
  padding: 0 22rpx;
  border-radius: 26rpx;
  background: #eef6f2;
  color: #4e8f7d;
  font-size: 21rpx;
  font-weight: 700;
}

.spot-recommendation__action--pressed {
  opacity: 0.65;
}
</style>
