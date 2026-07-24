<script setup lang="ts">
import { ref } from 'vue'
import type { GuideSpot, SpotCategoryId } from '../../types/guide'

defineProps<{
  spots: readonly GuideSpot[]
}>()

const emit = defineEmits<{
  select: [spotId: string]
}>()

const failedImages = ref<readonly string[]>([])

const categoryLabels: Readonly<Record<SpotCategoryId, string>> = {
  architecture: '建筑景观',
  sports: '运动场馆',
  study: '学习空间',
  green: '校园绿地',
}

function handleImageError(imagePath: string) {
  if (!failedImages.value.includes(imagePath)) {
    failedImages.value = [...failedImages.value, imagePath]
  }
}
</script>

<template>
  <view class="related-spots">
    <text class="related-spots__title">周边相关点位</text>
    <scroll-view class="related-spots__scroll" scroll-x :show-scrollbar="false">
      <view class="related-spots__list">
        <view
          v-for="spot in spots"
          :key="spot.id"
          class="related-spots__card"
          @tap="emit('select', spot.id)"
        >
          <view class="related-spots__media">
            <image
              v-if="!failedImages.includes(spot.coverImage)"
              class="related-spots__image"
              :src="spot.coverImage"
              :alt="spot.name"
              mode="aspectFill"
              @error="handleImageError(spot.coverImage)"
            />
            <view v-else class="related-spots__placeholder">
              <text>暂无图片</text>
            </view>
          </view>
          <text class="related-spots__name">{{ spot.name }}</text>
          <text class="related-spots__meta">
            {{ spot.tags[0] || categoryLabels[spot.category] }}
          </text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<style scoped>
.related-spots {
  margin-top: 38rpx;
  padding: 0 0 0 36rpx;
}

.related-spots__title {
  display: block;
  color: #292724;
  font-size: 38rpx;
  font-weight: 700;
  line-height: 54rpx;
}

.related-spots__scroll {
  width: 100%;
  margin-top: 18rpx;
  white-space: nowrap;
}

.related-spots__list {
  display: inline-flex;
  gap: 18rpx;
  box-sizing: border-box;
  padding-right: 36rpx;
}

.related-spots__card {
  display: flex;
  box-sizing: border-box;
  width: 226rpx;
  overflow: hidden;
  flex: none;
  flex-direction: column;
  padding-bottom: 18rpx;
  border-radius: 20rpx;
  background: #ffffff;
  box-shadow: 0 5rpx 18rpx rgba(184, 174, 165, 0.13);
}

.related-spots__media,
.related-spots__image,
.related-spots__placeholder {
  width: 100%;
  height: 130rpx;
}

.related-spots__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eee8e1;
  color: #8b847c;
  font-size: 21rpx;
}

.related-spots__name,
.related-spots__meta {
  overflow: hidden;
  padding: 0 18rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-spots__name {
  margin-top: 15rpx;
  color: #3f3c39;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 40rpx;
}

.related-spots__meta {
  margin-top: 4rpx;
  color: #838078;
  font-size: 22rpx;
  line-height: 32rpx;
}
</style>
