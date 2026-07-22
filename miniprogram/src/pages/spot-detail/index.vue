<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'
import RelatedSpotList from '../../components/spot-detail/RelatedSpotList.vue'
import SpotCheckinTip from '../../components/spot-detail/SpotCheckinTip.vue'
import SpotDetailActions from '../../components/spot-detail/SpotDetailActions.vue'
import SpotDetailErrorState from '../../components/spot-detail/SpotDetailErrorState.vue'
import SpotDetailHeader from '../../components/spot-detail/SpotDetailHeader.vue'
import SpotDetailIntro from '../../components/spot-detail/SpotDetailIntro.vue'
import SpotGallery from '../../components/spot-detail/SpotGallery.vue'
import SpotVisitInfo from '../../components/spot-detail/SpotVisitInfo.vue'
import { guideDemoData } from '../../mocks/guide'
import { buildCheckinOverview, recordsDemoData } from '../../mocks/records'
import { mergeVideoDemoRecordSources } from '../../state/video-demo'
import type { GuideSpot } from '../../types/guide'
import type { SpotDetailPageStatus } from '../../types/spot-detail'

const pageStatus = ref<SpotDetailPageStatus>('missing-id')
const currentSpot = ref<GuideSpot | null>(null)
const isInRoute = ref(false)
const scrollTop = ref(0)

const spotById = new Map<string, GuideSpot>()
guideDemoData.spots.forEach((spot) => spotById.set(spot.id, spot))

const checkedSpotIds = computed(() => new Set(
  buildCheckinOverview(mergeVideoDemoRecordSources(recordsDemoData.records), guideDemoData.spots).checkedSpotIds,
))

const galleryImages = computed<readonly string[]>(() => {
  const spot = currentSpot.value
  if (!spot) return []

  const uniqueImages = new Set<string>()
  const imagePaths = [spot.coverImage, ...spot.gallery]
  imagePaths.forEach((imagePath) => {
    const normalizedPath = imagePath.trim()
    if (normalizedPath) uniqueImages.add(normalizedPath)
  })
  return [...uniqueImages]
})

const isCheckedIn = computed(
  () => currentSpot.value !== null && checkedSpotIds.value.has(currentSpot.value.id),
)

const relatedSpots = computed<readonly GuideSpot[]>(() => {
  const spot = currentSpot.value
  if (!spot) return []

  const resolved: GuideSpot[] = []
  const addedIds = new Set<string>()
  spot.relatedSpotIds.forEach((relatedSpotId) => {
    const relatedSpot = spotById.get(relatedSpotId)
    if (!relatedSpot || relatedSpot.id === spot.id || addedIds.has(relatedSpot.id)) return
    addedIds.add(relatedSpot.id)
    resolved.push(relatedSpot)
  })
  return resolved
})

function loadSpot(rawSpotId: string | undefined) {
  currentSpot.value = null
  scrollTop.value = 0

  if (!rawSpotId) {
    pageStatus.value = 'missing-id'
    return
  }

  let decodedSpotId = ''
  try {
    decodedSpotId = decodeURIComponent(rawSpotId).trim()
  } catch {
    pageStatus.value = 'not-found'
    return
  }

  if (!decodedSpotId) {
    pageStatus.value = 'missing-id'
    return
  }

  const spot = spotById.get(decodedSpotId)
  if (!spot || !spot.id.trim() || !spot.name.trim()) {
    pageStatus.value = 'not-found'
    return
  }

  currentSpot.value = spot
  isInRoute.value = spot.isInRoute
  pageStatus.value = 'ready'
}

onLoad((options) => {
  const rawSpotId = typeof options?.spotId === 'string' ? options.spotId : undefined
  loadSpot(rawSpotId)
})

function handleBack() {
  if (getCurrentPages().length > 1) {
    uni.navigateBack()
    return
  }
  uni.reLaunch({ url: '/pages/guide/index' })
}

function handleLocationRequest() {
  uni.showToast({
    title: '定位距离功能待接入',
    icon: 'none',
  })
}

function handleToggleRoute() {
  isInRoute.value = !isInRoute.value
  uni.showToast({
    title: isInRoute.value ? '已加入路线' : '已移出路线',
    icon: 'none',
  })
}

function handleOpenGuide() {
  uni.navigateTo({
    url: '/pages/guide/index',
  })
}

function handleRelatedSpotSelect(spotId: string) {
  uni.redirectTo({
    url: `/pages/spot-detail/index?spotId=${encodeURIComponent(spotId)}`,
  })
}
</script>

<template>
  <view class="spot-detail-page">
    <SpotDetailHeader title="点位详情" @back="handleBack" />

    <scroll-view
      class="spot-detail-page__scroll"
      scroll-y
      enable-back-to-top
      :scroll-top="scrollTop"
      :show-scrollbar="false"
    >
      <view v-if="pageStatus === 'ready' && currentSpot" class="spot-detail-page__content">
        <SpotGallery :images="galleryImages" :spot-name="currentSpot.name" />
        <SpotDetailIntro :spot="currentSpot" />
        <SpotVisitInfo
          :suggested-stay-text="currentSpot.suggestedStayText"
          :recommended-times="currentSpot.recommendedTimes"
          :is-checked-in="isCheckedIn"
          @request-location="handleLocationRequest"
        />
        <SpotCheckinTip
          v-if="currentSpot.checkinTip.trim()"
          :tip="currentSpot.checkinTip"
        />
        <RelatedSpotList
          v-if="relatedSpots.length > 0"
          :spots="relatedSpots"
          @select="handleRelatedSpotSelect"
        />
        <text class="spot-detail-page__demo-note">
          点位、打卡、路线与距离信息当前均为本地演示状态
        </text>
      </view>

      <SpotDetailErrorState v-else @back="handleBack" />
    </scroll-view>

    <SpotDetailActions
      v-if="pageStatus === 'ready' && currentSpot"
      :is-in-route="isInRoute"
      @toggle-route="handleToggleRoute"
      @open-guide="handleOpenGuide"
    />
  </view>
</template>

<style scoped>
.spot-detail-page {
  display: flex;
  box-sizing: border-box;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  flex-direction: column;
  background: #fbf6f0;
  color: #292724;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.spot-detail-page__scroll {
  min-height: 0;
  flex: 1;
}

.spot-detail-page__content {
  box-sizing: border-box;
  width: 100%;
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));
}

.spot-detail-page__demo-note {
  display: block;
  margin: 34rpx 36rpx 0;
  color: #968e86;
  font-size: 22rpx;
  line-height: 35rpx;
  text-align: center;
}
</style>
