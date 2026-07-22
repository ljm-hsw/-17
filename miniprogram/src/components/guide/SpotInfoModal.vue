<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { GuideSpot, SpotCategoryId, SpotDistanceState } from '../../types/guide'

const props = defineProps<{
  spot: GuideSpot
  isInRoute: boolean
  isCheckedIn: boolean
  distanceState: SpotDistanceState
}>()

const emit = defineEmits<{
  close: []
  viewDetails: [spotId: string]
  toggleRoute: [spot: GuideSpot]
  requestLocation: []
}>()

const categoryLabels: Record<SpotCategoryId, string> = {
  architecture: '建筑景观',
  sports: '运动场馆',
  study: '学习空间',
  green: '校园绿地',
}

const imageLoadFailed = ref(false)
const categoryLabel = computed(() => categoryLabels[props.spot.category])
const visibleTags = computed(() => props.spot.tags.slice(0, 4))
const previewImages = computed(() => [props.spot.coverImage, ...props.spot.gallery])

const systemInfo = uni.getSystemInfoSync()
const windowHeight = systemInfo.windowHeight || systemInfo.screenHeight
const statusBarHeight = systemInfo.statusBarHeight ?? 20
let protectedTop = statusBarHeight + 56

try {
  const menuButton = uni.getMenuButtonBoundingClientRect()
  if (menuButton.bottom > 0) {
    protectedTop = menuButton.bottom + 12
  }
} catch {
  protectedTop = statusBarHeight + 56
}

const safeBottom = Math.max(0, windowHeight - (systemInfo.safeArea?.bottom ?? windowHeight))
const protectedBottom = safeBottom + 12
const availableHeight = Math.max(280, windowHeight - protectedTop - protectedBottom)
const modalHeight = Math.min(560, availableHeight)

const layerStyle = {
  paddingTop: `${protectedTop}px`,
  paddingBottom: `${protectedBottom}px`,
}

const modalStyle = {
  height: `${modalHeight}px`,
}

watch(
  () => props.spot.id,
  () => {
    imageLoadFailed.value = false
  },
)

function handleImageError() {
  imageLoadFailed.value = true
}

function previewSpotImages() {
  if (imageLoadFailed.value) return

  uni.previewImage({
    current: props.spot.coverImage,
    urls: previewImages.value,
    fail: () => {
      uni.showToast({
        title: '图片预览暂不可用',
        icon: 'none',
      })
    },
  })
}

function handleDistanceTap() {
  if (props.distanceState.status === 'available') return

  if (props.distanceState.status === 'loading') {
    uni.showToast({
      title: '正在获取位置',
      icon: 'none',
    })
    return
  }

  emit('requestLocation')
}
</script>

<template>
  <view class="spot-modal-layer" :style="layerStyle" @tap="$emit('close')">
    <view class="spot-modal" :style="modalStyle" @tap.stop>
      <view class="spot-modal__heading">
        <text class="spot-modal__title">{{ spot.name }}</text>
        <view
          class="spot-modal__close"
          hover-class="spot-modal__close--pressed"
          aria-label="关闭"
          @tap="$emit('close')"
        >
          <text>×</text>
        </view>
      </view>

      <scroll-view class="spot-modal__content" scroll-y>
        <view class="spot-modal__tags">
          <text class="spot-modal__tag spot-modal__tag--category">{{ categoryLabel }}</text>
          <text v-for="tag in visibleTags" :key="tag" class="spot-modal__tag">{{ tag }}</text>
        </view>

        <view class="spot-modal__media" @tap="previewSpotImages">
          <image
            v-if="!imageLoadFailed"
            class="spot-modal__image"
            :src="spot.coverImage"
            :alt="spot.name"
            mode="aspectFill"
            @error="handleImageError"
          />
          <view v-else class="spot-modal__image-placeholder">
            <text>图片暂不可用</text>
          </view>
        </view>

        <text class="spot-modal__summary">{{ spot.summary }}</text>

        <view v-if="spot.isRecommended" class="spot-modal__recommendation">
          <text class="spot-modal__recommendation-title">推荐理由</text>
          <text class="spot-modal__recommendation-text">{{ spot.recommendationReason }}</text>
        </view>

        <view class="spot-modal__divider" />

        <view class="spot-modal__meta">
          <view class="spot-modal__meta-row">
            <text>推荐停留时间</text>
            <text>{{ spot.suggestedStayText }}</text>
          </view>
          <view class="spot-modal__meta-row">
            <text>是否推荐点位</text>
            <text :class="{ 'spot-modal__recommended': spot.isRecommended }">
              {{ spot.isRecommended ? '推荐' : '普通点位' }}
            </text>
          </view>
          <view class="spot-modal__meta-row">
            <text>距离信息</text>
            <view
              class="spot-modal__distance"
              :class="{ 'spot-modal__distance--action': distanceState.status !== 'available' }"
              @tap="handleDistanceTap"
            >
              <text>{{ distanceState.label }}</text>
              <text v-if="distanceState.status !== 'available'" class="spot-modal__distance-arrow">›</text>
            </view>
          </view>
          <view class="spot-modal__meta-row">
            <text>打卡状态</text>
            <text :class="{ 'spot-modal__checked': isCheckedIn }">
              {{ isCheckedIn ? '已打卡' : '未打卡' }}
            </text>
          </view>
        </view>
      </scroll-view>

      <view class="spot-modal__actions">
        <view
          class="spot-modal__button spot-modal__button--secondary"
          hover-class="spot-modal__button--pressed"
          @tap="$emit('viewDetails', spot.id)"
        >
          <text>查看详情</text>
        </view>
        <view
          class="spot-modal__button spot-modal__button--primary"
          :class="{
            'spot-modal__button--joined': isInRoute,
            'spot-modal__button--locked': isCheckedIn,
          }"
          hover-class="spot-modal__button--pressed"
          @tap="!isCheckedIn && $emit('toggleRoute', spot)"
        >
          <text>{{ isCheckedIn ? '已在路线' : isInRoute ? '移出路线' : '加入路线' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.spot-modal-layer {
  position: fixed;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding-right: 32rpx;
  padding-left: 32rpx;
  background: rgba(29, 33, 30, 0.44);
  inset: 0;
}

.spot-modal {
  display: flex;
  box-sizing: border-box;
  width: calc(100vw - 64rpx);
  max-width: 654rpx;
  max-height: 100%;
  flex-direction: column;
  padding: 30rpx 42rpx 38rpx;
  border-radius: 40rpx;
  background: #fffefc;
  box-shadow: 0 14rpx 42rpx rgba(77, 71, 63, 0.24);
}

.spot-modal__heading,
.spot-modal__tags,
.spot-modal__meta-row,
.spot-modal__actions {
  display: flex;
  align-items: center;
}

.spot-modal__heading {
  flex: none;
  justify-content: space-between;
}

.spot-modal__title {
  min-width: 0;
  flex: 1;
  color: #171816;
  font-size: 42rpx;
  font-weight: 700;
  line-height: 62rpx;
}

.spot-modal__close {
  display: flex;
  width: 64rpx;
  height: 64rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  margin-left: 18rpx;
  border-radius: 50%;
  background: #f1ebe3;
  color: #6d675f;
  font-size: 49rpx;
  font-weight: 400;
  line-height: 64rpx;
}

.spot-modal__close--pressed {
  opacity: 0.66;
}

.spot-modal__content {
  height: 0;
  min-height: 0;
  flex: 1;
  overflow: hidden;
}

.spot-modal__tags {
  flex-wrap: wrap;
  gap: 10rpx 12rpx;
  padding-top: 4rpx;
}

.spot-modal__tag {
  box-sizing: border-box;
  flex-shrink: 0;
  padding: 7rpx 20rpx;
  border-radius: 25rpx;
  background: #f5efe7;
  color: #766f67;
  font-size: 23rpx;
  font-weight: 500;
  line-height: 34rpx;
  white-space: nowrap;
  word-break: keep-all;
}

.spot-modal__tag--category {
  background: #e7f5f0;
  color: #277c6b;
  font-weight: 700;
}

.spot-modal__media {
  width: 100%;
  height: 300rpx;
  margin-top: 20rpx;
  overflow: hidden;
  border-radius: 26rpx;
  background: #f2eee8;
}

.spot-modal__image,
.spot-modal__image-placeholder {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
}

.spot-modal__image-placeholder {
  color: #99928a;
  font-size: 25rpx;
}

.spot-modal__summary {
  display: block;
  margin-top: 22rpx;
  color: #5c5852;
  font-size: 27rpx;
  line-height: 44rpx;
}

.spot-modal__recommendation {
  margin-top: 20rpx;
  padding: 18rpx 20rpx;
  border-radius: 20rpx;
  background: #f3faf7;
}

.spot-modal__recommendation-title,
.spot-modal__recommendation-text {
  display: block;
}

.spot-modal__recommendation-title {
  color: #277c6b;
  font-size: 24rpx;
  font-weight: 700;
}

.spot-modal__recommendation-text {
  margin-top: 6rpx;
  color: #52625d;
  font-size: 24rpx;
  line-height: 38rpx;
}

.spot-modal__divider {
  height: 2rpx;
  margin-top: 24rpx;
  background: #ece5dc;
}

.spot-modal__meta {
  padding: 12rpx 0 8rpx;
}

.spot-modal__meta-row {
  justify-content: space-between;
  min-height: 62rpx;
  color: #4d4944;
  font-size: 26rpx;
  font-weight: 500;
}

.spot-modal__meta-row > text:last-child,
.spot-modal__meta-row > view:last-child {
  max-width: 330rpx;
  text-align: right;
}

.spot-modal__checked,
.spot-modal__recommended {
  color: #3f9d87;
  font-weight: 700;
}

.spot-modal__distance {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 7rpx;
  color: #4d4944;
}

.spot-modal__distance--action {
  min-height: 54rpx;
  color: #278c79;
  font-weight: 700;
}

.spot-modal__distance-arrow {
  font-size: 34rpx;
  font-weight: 400;
}

.spot-modal__actions {
  flex: none;
  gap: 30rpx;
  justify-content: space-between;
  padding-top: 24rpx;
}

.spot-modal__button {
  display: flex;
  box-sizing: border-box;
  height: 92rpx;
  flex: 1;
  align-items: center;
  justify-content: center;
  border-radius: 48rpx;
  font-size: 29rpx;
  font-weight: 700;
}

.spot-modal__button--secondary {
  border: 2rpx solid #ddd5ca;
  color: #4d4944;
}

.spot-modal__button--primary {
  background: #e87e3e;
  box-shadow: 0 7rpx 16rpx rgba(197, 107, 52, 0.22);
  color: #ffffff;
}

.spot-modal__button--joined {
  background: #49aa96;
  box-shadow: 0 7rpx 16rpx rgba(63, 157, 135, 0.2);
}

.spot-modal__button--locked {
  border-color: #d9e4df;
  background: #f0f3f1;
  color: #728079;
}

.spot-modal__button--pressed {
  opacity: 0.76;
}
</style>
