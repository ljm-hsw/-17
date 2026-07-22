<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { GuideSpot, SpotCategoryId } from '../../types/guide'

const props = defineProps<{
  spot: GuideSpot
  isCheckedIn: boolean
  isInRoute: boolean
}>()

const emit = defineEmits<{
  viewDetails: [spotId: string]
  toggleRoute: [spotId: string]
}>()

const imageLoadFailed = ref(false)

const categoryLabels: Readonly<Record<SpotCategoryId, string>> = {
  architecture: '建筑景观',
  sports: '运动场馆',
  study: '学习空间',
  green: '校园绿地',
}

const visibleTags = computed(() => props.spot.tags.slice(0, 3))

watch(
  () => props.spot.id,
  () => {
    imageLoadFailed.value = false
  },
)
</script>

<template>
  <view class="spot-card" @tap="emit('viewDetails', spot.id)">
    <view class="spot-card__media">
      <image
        v-if="!imageLoadFailed"
        class="spot-card__image"
        :src="spot.coverImage"
        :alt="spot.name"
        mode="aspectFill"
        @error="imageLoadFailed = true"
      />
      <view v-else class="spot-card__image-placeholder">
        <text>图片暂不可用</text>
      </view>
      <view class="spot-card__recommended">
        <text>推荐</text>
      </view>
    </view>

    <view class="spot-card__content">
      <view class="spot-card__heading">
        <text class="spot-card__name">{{ spot.name }}</text>
        <text class="spot-card__category">{{ categoryLabels[spot.category] }}</text>
      </view>

      <view class="spot-card__tags">
        <text v-for="tag in visibleTags" :key="tag" class="spot-card__tag">
          {{ tag }}
        </text>
      </view>

      <text class="spot-card__summary">{{ spot.summary }}</text>
      <view class="spot-card__reason">
        <text class="spot-card__reason-label">推荐理由</text>
        <text class="spot-card__reason-text">{{ spot.recommendationReason }}</text>
      </view>

      <view class="spot-card__meta">
        <text>建议停留 {{ spot.suggestedStayText }}</text>
        <text
          class="spot-card__checkin"
          :class="{ 'spot-card__checkin--done': isCheckedIn }"
        >
          {{ isCheckedIn ? '已打卡' : '未打卡' }}
        </text>
      </view>

      <view class="spot-card__actions">
        <view
          class="spot-card__button spot-card__button--secondary"
          @tap.stop="emit('viewDetails', spot.id)"
        >
          <text>查看详情</text>
        </view>
        <view
          class="spot-card__button spot-card__button--primary"
          :class="{
            'spot-card__button--joined': isInRoute,
            'spot-card__button--locked': isCheckedIn,
          }"
          @tap.stop="!isCheckedIn && emit('toggleRoute', spot.id)"
        >
          <text>{{ isCheckedIn ? '已在路线' : isInRoute ? '已加入路线' : '加入路线' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.spot-card {
  display: flex;
  box-sizing: border-box;
  width: 100%;
  min-height: 398rpx;
  overflow: hidden;
  border: 1rpx solid rgba(47, 96, 80, 0.07);
  border-radius: 28rpx;
  background: #fffcf8;
  box-shadow: 0 13rpx 32rpx rgba(81, 66, 49, 0.09);
}

.spot-card__media {
  position: relative;
  flex: 0 0 232rpx;
  min-height: 398rpx;
  overflow: hidden;
  background: #e5eee9;
}

.spot-card__image,
.spot-card__image-placeholder {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.spot-card__image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #769087;
  font-size: 23rpx;
}

.spot-card__recommended {
  position: absolute;
  top: 18rpx;
  left: 16rpx;
  padding: 8rpx 15rpx;
  border-radius: 999rpx;
  background: rgba(24, 84, 67, 0.9);
  color: #ffffff;
  font-size: 21rpx;
  font-weight: 600;
  line-height: 1;
}

.spot-card__content {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
  padding: 22rpx 22rpx 20rpx;
}

.spot-card__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12rpx;
}

.spot-card__name {
  min-width: 0;
  color: #183c32;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.25;
}

.spot-card__category {
  flex: none;
  padding-top: 5rpx;
  color: #5e7c71;
  font-size: 21rpx;
  white-space: nowrap;
}

.spot-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-top: 12rpx;
}

.spot-card__tag {
  flex-shrink: 0;
  padding: 6rpx 11rpx;
  border-radius: 999rpx;
  background: #e8f4ef;
  color: #347e69;
  font-size: 20rpx;
  line-height: 1;
  white-space: nowrap;
  word-break: keep-all;
}

.spot-card__summary,
.spot-card__reason-text {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.spot-card__summary {
  margin-top: 13rpx;
  color: #4f635c;
  font-size: 23rpx;
  line-height: 1.5;
}

.spot-card__reason {
  display: flex;
  align-items: flex-start;
  gap: 10rpx;
  margin-top: 11rpx;
}

.spot-card__reason-label {
  flex: none;
  color: #c17f3b;
  font-size: 21rpx;
  font-weight: 600;
  line-height: 1.5;
}

.spot-card__reason-text {
  color: #765e47;
  font-size: 21rpx;
  line-height: 1.5;
}

.spot-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  margin-top: auto;
  padding-top: 12rpx;
  color: #688078;
  font-size: 21rpx;
}

.spot-card__checkin {
  flex: none;
  color: #9b8c7d;
}

.spot-card__checkin--done {
  color: #2e997c;
  font-weight: 600;
}

.spot-card__actions {
  display: flex;
  gap: 12rpx;
  margin-top: 15rpx;
}

.spot-card__button {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  height: 60rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.spot-card__button--secondary {
  border: 1rpx solid #45b297;
  background: #ffffff;
  color: #2f8f76;
}

.spot-card__button--primary {
  border: 1rpx solid #45b297;
  background: #45b297;
  color: #ffffff;
}

.spot-card__button--joined {
  border-color: #cce7df;
  background: #e8f4ef;
  color: #287b65;
}

.spot-card__button--locked {
  border-color: #d9e4df;
  background: #f0f3f1;
  color: #728079;
}

@media (max-width: 350px) {
  .spot-card__media {
    flex-basis: 208rpx;
  }

  .spot-card__content {
    padding-right: 18rpx;
    padding-left: 18rpx;
  }
}
</style>
