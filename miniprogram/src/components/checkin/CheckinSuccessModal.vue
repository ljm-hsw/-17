<script setup lang="ts">
import { ref, watch } from 'vue'
import type { CheckinSuccessData } from '../../types/checkin-success'
import type { GuideSpot } from '../../types/guide'

const props = defineProps<{
  checkinData: CheckinSuccessData
  spot: GuideSpot
}>()

const emit = defineEmits<{
  close: []
  dismiss: []
  startPhoto: [data: CheckinSuccessData]
  viewSpot: [spotId: string]
}>()

const coverLoadFailed = ref(false)
const poseLoadFailed = ref(false)

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
const calculatedAvailableHeight = windowHeight - protectedTop - protectedBottom
const availableHeight = calculatedAvailableHeight > 0 ? calculatedAvailableHeight : windowHeight * 0.8
const modalHeight = Math.min(680, availableHeight)

const layerStyle = {
  paddingTop: `${protectedTop}px`,
  paddingBottom: `${protectedBottom}px`,
}

const modalStyle = {
  height: `${modalHeight}px`,
}

watch(
  () => [props.spot.id, props.checkinData.pose.id],
  () => {
    coverLoadFailed.value = false
    poseLoadFailed.value = false
  },
)
</script>

<template>
  <view class="checkin-success-layer" :style="layerStyle" @tap="emit('close')">
    <view class="checkin-success-modal" :style="modalStyle" @tap.stop>
      <view class="checkin-success-modal__heading">
        <view class="checkin-success-modal__success">
          <view class="checkin-success-modal__check"><text>✓</text></view>
          <text class="checkin-success-modal__title">打卡成功</text>
        </view>
        <view
          class="checkin-success-modal__close"
          aria-label="关闭"
          hover-class="checkin-success-modal__pressed"
          @tap="emit('close')"
        >
          <text>×</text>
        </view>
      </view>

      <scroll-view class="checkin-success-modal__scroll" scroll-y :show-scrollbar="false">
        <view class="checkin-success-modal__content">
          <text class="checkin-success-modal__welcome">欢迎来到{{ spot.name }}</text>

          <view class="checkin-success-modal__cover">
            <image
              v-if="!coverLoadFailed"
              class="checkin-success-modal__cover-image"
              :src="spot.coverImage"
              :alt="spot.name"
              mode="aspectFill"
              @error="coverLoadFailed = true"
            />
            <view v-else class="checkin-success-modal__placeholder">
              <text>{{ spot.name }}</text>
              <text>图片暂不可用</text>
            </view>
          </view>

          <view class="checkin-success-modal__meta">
            <view class="checkin-success-modal__meta-row">
              <text class="checkin-success-modal__meta-label">打卡时间</text>
              <text class="checkin-success-modal__meta-value">
                {{ checkinData.checkedAtLabel }}
              </text>
            </view>
            <view class="checkin-success-modal__meta-row">
              <text class="checkin-success-modal__meta-label">打卡方式</text>
              <text class="checkin-success-modal__meta-value">
                {{ checkinData.methodLabel }}
              </text>
            </view>
          </view>

          <view class="checkin-success-modal__progress">
            <text>当前完成进度</text>
            <text class="checkin-success-modal__progress-value">
              已完成 {{ checkinData.checkedCount }} / {{ checkinData.totalCount }}
            </text>
          </view>
          <view class="checkin-success-modal__digital-card">
            <text class="checkin-success-modal__section-eyebrow">数字点位卡</text>
            <text class="checkin-success-modal__digital-title">
              已获得“{{ spot.name }}”数字卡
            </text>
            <view class="checkin-success-modal__view-spot" @tap="emit('viewSpot', spot.id)">
              <text>查看点位</text>
              <text>›</text>
            </view>
          </view>

          <view class="checkin-success-modal__pose-card">
            <view class="checkin-success-modal__pose-media">
              <image
                v-if="!poseLoadFailed"
                class="checkin-success-modal__pose-image"
                :src="checkinData.pose.image"
                :alt="checkinData.pose.name"
                mode="aspectFill"
                @error="poseLoadFailed = true"
              />
              <view v-else class="checkin-success-modal__placeholder">
                <text>姿势图片暂不可用</text>
              </view>
            </view>
            <view class="checkin-success-modal__pose-info">
              <text class="checkin-success-modal__section-eyebrow">本次随机拍照姿势</text>
              <text class="checkin-success-modal__pose-name">{{ checkinData.pose.name }}</text>
              <text class="checkin-success-modal__pose-instruction">
                {{ checkinData.pose.instruction }}
              </text>
            </view>
          </view>
        </view>
      </scroll-view>

      <view class="checkin-success-modal__actions">
        <view
          class="checkin-success-modal__button checkin-success-modal__button--primary"
          hover-class="checkin-success-modal__pressed"
          @tap="emit('startPhoto', checkinData)"
        >
          <text>开始拍照</text>
        </view>
        <view
          class="checkin-success-modal__button checkin-success-modal__button--secondary"
          hover-class="checkin-success-modal__pressed"
          @tap="emit('dismiss')"
        >
          <text>稍后再拍</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.checkin-success-layer {
  position: fixed;
  z-index: 80;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding-right: 32rpx;
  padding-left: 32rpx;
  background: rgba(26, 33, 29, 0.5);
  inset: 0;
}

.checkin-success-modal {
  display: flex;
  box-sizing: border-box;
  width: calc(100vw - 64rpx);
  max-width: 670rpx;
  max-height: 100%;
  overflow: hidden;
  flex-direction: column;
  padding: 28rpx 30rpx 30rpx;
  border-radius: 40rpx;
  background: #fffefc;
  box-shadow: 0 18rpx 48rpx rgba(65, 54, 43, 0.25);
}

.checkin-success-modal__heading,
.checkin-success-modal__success,
.checkin-success-modal__meta-row,
.checkin-success-modal__progress,
.checkin-success-modal__view-spot,
.checkin-success-modal__pose-card,
.checkin-success-modal__actions {
  display: flex;
  align-items: center;
}

.checkin-success-modal__heading {
  flex: none;
  justify-content: space-between;
  gap: 18rpx;
}

.checkin-success-modal__success {
  min-width: 0;
  gap: 18rpx;
}

.checkin-success-modal__check {
  display: flex;
  width: 66rpx;
  height: 66rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #3daf91;
  color: #ffffff;
  font-size: 38rpx;
  font-weight: 800;
}

.checkin-success-modal__title,
.checkin-success-modal__welcome,
.checkin-success-modal__meta-label,
.checkin-success-modal__meta-value,
.checkin-success-modal__section-eyebrow,
.checkin-success-modal__digital-title,
.checkin-success-modal__pose-name,
.checkin-success-modal__pose-instruction {
  display: block;
}

.checkin-success-modal__title {
  color: #1f2824;
  font-size: 38rpx;
  font-weight: 800;
  line-height: 50rpx;
}

.checkin-success-modal__close {
  display: flex;
  width: 60rpx;
  height: 60rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f1ebe3;
  color: #6d675f;
  font-size: 46rpx;
  line-height: 60rpx;
}

.checkin-success-modal__scroll {
  height: 0;
  min-height: 0;
  flex: 1;
  margin-top: 22rpx;
}

.checkin-success-modal__content {
  padding-bottom: 8rpx;
}

.checkin-success-modal__welcome {
  display: block;
  color: #21483d;
  font-size: 36rpx;
  font-weight: 700;
  line-height: 50rpx;
  word-break: keep-all;
  white-space: nowrap;
}

.checkin-success-modal__cover,
.checkin-success-modal__cover-image,
.checkin-success-modal__cover .checkin-success-modal__placeholder {
  width: 100%;
  height: 288rpx;
}

.checkin-success-modal__cover {
  overflow: hidden;
  box-sizing: border-box;
  margin-top: 18rpx;
  border-radius: 22rpx;
  background: #eee8e1;
}

.checkin-success-modal__cover-image {
  display: block;
}

.checkin-success-modal__cover .checkin-success-modal__placeholder {
  flex-direction: column;
  gap: 8rpx;
}

.checkin-success-modal__meta {
  margin-top: 18rpx;
  padding: 16rpx 22rpx;
  border-radius: 20rpx;
  background: #fbf6f0;
}

.checkin-success-modal__meta-row {
  justify-content: space-between;
  gap: 20rpx;
  min-height: 42rpx;
}

.checkin-success-modal__meta-row + .checkin-success-modal__meta-row {
  margin-top: 6rpx;
}

.checkin-success-modal__meta-label {
  flex: none;
  color: #8a8178;
  font-size: 23rpx;
}

.checkin-success-modal__meta-value {
  min-width: 0;
  color: #4d554f;
  font-size: 24rpx;
  font-weight: 600;
  text-align: right;
}

.checkin-success-modal__progress {
  justify-content: space-between;
  margin-top: 18rpx;
  padding: 20rpx 24rpx;
  border-radius: 20rpx;
  background: #edf7f3;
  color: #577068;
  font-size: 25rpx;
}

.checkin-success-modal__progress-value {
  color: #27866f;
  font-size: 28rpx;
  font-weight: 800;
  white-space: nowrap;
}

.checkin-success-modal__digital-card {
  position: relative;
  margin-top: 18rpx;
  padding: 22rpx 110rpx 22rpx 24rpx;
  border: 1rpx solid rgba(219, 143, 64, 0.18);
  border-radius: 20rpx;
  background: #fff7ed;
}

.checkin-success-modal__section-eyebrow {
  color: #b37334;
  font-size: 21rpx;
  font-weight: 700;
  line-height: 32rpx;
}

.checkin-success-modal__digital-title {
  margin-top: 5rpx;
  color: #5f4935;
  font-size: 27rpx;
  font-weight: 700;
  line-height: 40rpx;
}

.checkin-success-modal__view-spot {
  position: absolute;
  top: 50%;
  right: 20rpx;
  color: #2d927b;
  font-size: 23rpx;
  font-weight: 700;
  transform: translateY(-50%);
  white-space: nowrap;
}

.checkin-success-modal__pose-card {
  align-items: stretch;
  gap: 22rpx;
  margin-top: 18rpx;
  padding: 18rpx;
  border-radius: 24rpx;
  background: #f4f8f6;
}

.checkin-success-modal__pose-media,
.checkin-success-modal__pose-image,
.checkin-success-modal__pose-media .checkin-success-modal__placeholder {
  width: 190rpx;
  height: 190rpx;
}

.checkin-success-modal__pose-media {
  flex: none;
  overflow: hidden;
  border-radius: 20rpx;
  background: #e9efec;
}

.checkin-success-modal__pose-image {
  display: block;
}

.checkin-success-modal__pose-info {
  display: flex;
  min-width: 0;
  flex: 1;
  justify-content: center;
  flex-direction: column;
}

.checkin-success-modal__pose-info .checkin-success-modal__section-eyebrow {
  color: #4c8e7d;
}

.checkin-success-modal__pose-name {
  margin-top: 7rpx;
  color: #243c34;
  font-size: 31rpx;
  font-weight: 800;
  line-height: 44rpx;
}

.checkin-success-modal__pose-instruction {
  margin-top: 7rpx;
  color: #63726d;
  font-size: 23rpx;
  line-height: 36rpx;
  overflow-wrap: anywhere;
}

.checkin-success-modal__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eee8e1;
  color: #8c857e;
  font-size: 21rpx;
  text-align: center;
}

.checkin-success-modal__actions {
  flex: none;
  gap: 18rpx;
  padding-top: 22rpx;
}

.checkin-success-modal__button {
  display: flex;
  height: 82rpx;
  flex: 1;
  align-items: center;
  justify-content: center;
  border-radius: 42rpx;
  font-size: 27rpx;
  font-weight: 700;
  white-space: nowrap;
}

.checkin-success-modal__button--primary {
  background: #e99342;
  box-shadow: 0 6rpx 16rpx rgba(233, 147, 66, 0.2);
  color: #ffffff;
}

.checkin-success-modal__button--secondary {
  border: 2rpx solid #d8d0c6;
  color: #625d57;
}

.checkin-success-modal__pressed {
  opacity: 0.72;
}
</style>
