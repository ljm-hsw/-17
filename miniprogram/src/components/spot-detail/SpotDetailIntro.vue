<script setup lang="ts">
import { computed } from 'vue'
import type { GuideSpot, SpotCategoryId } from '../../types/guide'

const props = defineProps<{
  spot: GuideSpot
}>()

const categoryLabels: Readonly<Record<SpotCategoryId, string>> = {
  architecture: '建筑景观',
  sports: '运动场馆',
  study: '学习空间',
  green: '校园绿地',
}

const categoryLabel = computed(() => categoryLabels[props.spot.category])
const hasSummary = computed(() => props.spot.summary.trim().length > 0)
const hasDescription = computed(() => props.spot.description.trim().length > 0)
const hasRecommendation = computed(
  () => props.spot.isRecommended && props.spot.recommendationReason.trim().length > 0,
)
</script>

<template>
  <view class="spot-detail-intro">
    <text class="spot-detail-intro__name">{{ spot.name }}</text>

    <view class="spot-detail-intro__tags">
      <text class="spot-detail-intro__tag spot-detail-intro__tag--category">
        {{ categoryLabel }}
      </text>
      <text v-for="tag in spot.tags" :key="tag" class="spot-detail-intro__tag">
        {{ tag }}
      </text>
    </view>

    <text v-if="hasSummary" class="spot-detail-intro__summary">{{ spot.summary }}</text>

    <view v-if="hasRecommendation" class="spot-detail-intro__recommendation">
      <text class="spot-detail-intro__section-title">推荐理由</text>
      <text class="spot-detail-intro__section-text">{{ spot.recommendationReason }}</text>
    </view>

    <view v-if="hasDescription" class="spot-detail-intro__description">
      <text class="spot-detail-intro__section-title">详细介绍</text>
      <text class="spot-detail-intro__section-text spot-detail-intro__section-text--long">
        {{ spot.description }}
      </text>
    </view>
  </view>
</template>

<style scoped>
.spot-detail-intro {
  padding: 34rpx 36rpx 0;
}

.spot-detail-intro__name {
  display: block;
  color: #22211f;
  font-size: 46rpx;
  font-weight: 700;
  line-height: 66rpx;
  overflow-wrap: anywhere;
}

.spot-detail-intro__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}

.spot-detail-intro__tag {
  box-sizing: border-box;
  flex-shrink: 0;
  padding: 9rpx 18rpx;
  border-radius: 27rpx;
  background: #f7eee0;
  color: #8f6d4e;
  font-size: 24rpx;
  font-weight: 500;
  line-height: 34rpx;
  white-space: nowrap;
  word-break: keep-all;
}

.spot-detail-intro__tag--category {
  background: #e3f2f0;
  color: #2c9182;
  font-weight: 700;
}

.spot-detail-intro__summary {
  display: block;
  margin-top: 26rpx;
  color: #55514d;
  font-size: 27rpx;
  line-height: 46rpx;
  overflow-wrap: anywhere;
}

.spot-detail-intro__recommendation,
.spot-detail-intro__description {
  margin-top: 34rpx;
  padding: 26rpx 28rpx;
  border-radius: 24rpx;
}

.spot-detail-intro__recommendation {
  background: #edf7f3;
}

.spot-detail-intro__description {
  border: 1rpx solid rgba(154, 113, 66, 0.1);
  background: #fffdf9;
  box-shadow: 0 5rpx 18rpx rgba(135, 118, 101, 0.06);
}

.spot-detail-intro__section-title,
.spot-detail-intro__section-text {
  display: block;
}

.spot-detail-intro__section-title {
  color: #292724;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 44rpx;
}

.spot-detail-intro__recommendation .spot-detail-intro__section-title {
  color: #287f6c;
}

.spot-detail-intro__section-text {
  margin-top: 12rpx;
  color: #5a5752;
  font-size: 26rpx;
  line-height: 44rpx;
  overflow-wrap: anywhere;
  white-space: pre-line;
}

.spot-detail-intro__section-text--long {
  line-height: 47rpx;
}
</style>
