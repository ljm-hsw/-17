<script setup lang="ts">
import { computed, ref } from 'vue'
import RecommendationFilters from '../../components/recommendations/RecommendationFilters.vue'
import RecommendedSpotCard from '../../components/recommendations/RecommendedSpotCard.vue'
import RecommendationsEmptyState from '../../components/recommendations/RecommendationsEmptyState.vue'
import RecommendationsHeader from '../../components/recommendations/RecommendationsHeader.vue'
import { guideDemoData } from '../../mocks/guide'
import { buildCheckinOverview, recordsDemoData } from '../../mocks/records'
import {
  addSpotToRoute,
  isSpotInRoute,
  removeSpotFromRoute,
  routePlanState,
} from '../../state/route-plan'
import { mergeVideoDemoRecordSources } from '../../state/video-demo'
import type {
  RecommendationFilterId,
  RecommendationFilterOption,
  RecommendationListItem,
} from '../../types/recommendations'

const filterOptions: readonly RecommendationFilterOption[] = [
  { id: 'all', label: '全部' },
  { id: 'architecture', label: '建筑景观' },
  { id: 'study', label: '学习空间' },
  { id: 'sports', label: '运动场馆' },
  { id: 'green', label: '校园绿地' },
  { id: 'checked', label: '已打卡' },
  { id: 'unchecked', label: '未打卡' },
]

const activeFilterId = ref<RecommendationFilterId>('all')

const recommendedSpots = computed(() =>
  guideDemoData.spots.filter((spot) => spot.isRecommended),
)

const checkedSpotIds = computed(() => new Set(
  buildCheckinOverview(mergeVideoDemoRecordSources(recordsDemoData.records), guideDemoData.spots).checkedSpotIds,
))

const recommendationItems = computed<readonly RecommendationListItem[]>(() =>
  recommendedSpots.value.map((spot) => ({
    spot,
    isCheckedIn: checkedSpotIds.value.has(spot.id),
    isInRoute:
      checkedSpotIds.value.has(spot.id) || routePlanState.addedSpotIds.includes(spot.id),
  })),
)

const visibleItems = computed(() => {
  if (activeFilterId.value === 'all') {
    return recommendationItems.value
  }
  if (activeFilterId.value === 'checked') {
    return recommendationItems.value.filter((item) => item.isCheckedIn)
  }
  if (activeFilterId.value === 'unchecked') {
    return recommendationItems.value.filter((item) => !item.isCheckedIn)
  }
  return recommendationItems.value.filter(
    (item) => item.spot.category === activeFilterId.value,
  )
})

function handleBack() {
  uni.navigateBack()
}

function handleFilterSelect(id: RecommendationFilterId) {
  activeFilterId.value = id
}

function handleShowAll() {
  activeFilterId.value = 'all'
}

function handleViewDetails(spotId: string) {
  uni.navigateTo({
    url: `/pages/spot-detail/index?spotId=${encodeURIComponent(spotId)}`,
  })
}

function handleToggleRoute(spotId: string) {
  if (checkedSpotIds.value.has(spotId)) return

  const isInRoute = isSpotInRoute(spotId)
  if (isInRoute) {
    removeSpotFromRoute(spotId)
  } else {
    addSpotToRoute(spotId)
  }

  uni.showToast({
    title: isInRoute ? '已移出路线' : '已加入路线',
    icon: 'none',
  })
}
</script>

<template>
  <view class="recommendations-page">
    <RecommendationsHeader @back="handleBack" />
    <RecommendationFilters
      :options="filterOptions"
      :active-id="activeFilterId"
      @select="handleFilterSelect"
    />

    <scroll-view class="recommendations-page__scroll" scroll-y :show-scrollbar="false">
      <view v-if="visibleItems.length" class="recommendations-page__list">
        <RecommendedSpotCard
          v-for="item in visibleItems"
          :key="item.spot.id"
          :spot="item.spot"
          :is-checked-in="item.isCheckedIn"
          :is-in-route="item.isInRoute"
          @view-details="handleViewDetails"
          @toggle-route="handleToggleRoute"
        />
      </view>
      <RecommendationsEmptyState v-else @show-all="handleShowAll" />
    </scroll-view>
  </view>
</template>

<style scoped>
.recommendations-page {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #fbf6f0;
  color: #263f37;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.recommendations-page__scroll {
  flex: 1;
  min-height: 0;
}

.recommendations-page__list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  box-sizing: border-box;
  width: 100%;
  padding: 24rpx 24rpx calc(44rpx + env(safe-area-inset-bottom));
}
</style>
