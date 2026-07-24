<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'
import JourneyMaterialCard from '../../components/materials/JourneyMaterialCard.vue'
import MaterialsHeader from '../../components/materials/MaterialsHeader.vue'
import { guideDemoData } from '../../mocks/guide'
import { buildJourneyMaterials, materialsDemoData } from '../../mocks/materials'
import { recordsDemoData } from '../../mocks/records'
import { poseChallenges } from '../../mocks/checkin-success'
import { mergeVideoDemoCheckinRecords, videoDemoState } from '../../state/video-demo'
import type { PoseType } from '../../types/checkin-success'

const selectedSpotId = ref('')
const selectedPoseId = ref<PoseType | ''>('')
const selectedPoseName = computed(() => poseChallenges.find((pose) => pose.id === selectedPoseId.value)?.name ?? '')

const records = computed(() => mergeVideoDemoCheckinRecords(recordsDemoData.records))
const materials = computed(() => {
  const items = buildJourneyMaterials(
    records.value,
    guideDemoData.spots,
    videoDemoState.temporaryCheckins,
  )
  if (!selectedSpotId.value) return items
  return [...items].sort((left, right) => Number(right.spotId === selectedSpotId.value) - Number(left.spotId === selectedSpotId.value))
})

onLoad((options) => {
  selectedSpotId.value = typeof options?.spotId === 'string' ? options.spotId : ''
  const poseId = typeof options?.poseId === 'string' ? options.poseId : ''
  selectedPoseId.value = ['victory', 'hands-on-hips', 'arms-crossed'].includes(poseId)
    ? poseId as PoseType
    : ''
})

function handleBack() {
  if (getCurrentPages().length > 1) uni.navigateBack()
  else uni.reLaunch({ url: '/pages/index/index' })
}

function previewImage(image: string) {
  uni.previewImage({ current: image, urls: [image] })
}
</script>

<template>
  <view class="materials-page">
    <MaterialsHeader @back="handleBack" />
    <scroll-view class="materials-page__scroll" scroll-y :show-scrollbar="false">
      <view class="materials-page__content">
        <view class="materials-page__intro">
          <view class="materials-page__heading">
            <text class="materials-page__badge">{{ materialsDemoData.prototypeLabel }}</text>
            <text class="materials-page__count">当前素材 {{ materials.length }} 份</text>
          </view>
          <text class="materials-page__description">{{ materialsDemoData.description }}</text>
          <text class="materials-page__notice">{{ materialsDemoData.integrationNotice }}</text>
          <text v-if="selectedPoseName" class="materials-page__query-note">已接收姿势任务：{{ selectedPoseName }}</text>
        </view>

        <JourneyMaterialCard
          v-for="item in materials"
          :key="item.id"
          :item="item"
          @preview="previewImage"
        />
      </view>
    </scroll-view>
  </view>
</template>

<style scoped>
.materials-page { display: flex; width: 100%; height: 100vh; overflow: hidden; flex-direction: column; background: #fbf7f1; color: #2d302d; }
.materials-page__scroll { min-height: 0; flex: 1; }
.materials-page__content { display: flex; box-sizing: border-box; padding: 22rpx 30rpx calc(46rpx + env(safe-area-inset-bottom)); gap: 24rpx; flex-direction: column; }
.materials-page__intro { padding: 26rpx 28rpx; border-radius: 28rpx; background: linear-gradient(135deg, #edf8f3, #fffaf2); }
.materials-page__heading { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; }
.materials-page__badge { padding: 6rpx 16rpx; border-radius: 20rpx; background: #3f9b82; color: #fff; font-size: 21rpx; font-weight: 700; white-space: nowrap; }
.materials-page__count { color: #3b6f60; font-size: 25rpx; font-weight: 700; }
.materials-page__description { display: block; margin-top: 18rpx; color: #31473f; font-size: 29rpx; font-weight: 700; line-height: 44rpx; }
.materials-page__notice, .materials-page__query-note { display: block; margin-top: 8rpx; color: #7d7871; font-size: 23rpx; line-height: 36rpx; }
.materials-page__query-note { color: #438c78; }
</style>
