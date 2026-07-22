<script setup lang="ts">
import { computed, ref } from 'vue'
import CheckinSuccessModal from '../../components/checkin/CheckinSuccessModal.vue'
import CheckinRecordCard from '../../components/records/CheckinRecordCard.vue'
import CheckinStats from '../../components/records/CheckinStats.vue'
import CheckinStatusTabs from '../../components/records/CheckinStatusTabs.vue'
import ProductSyncCard from '../../components/records/ProductSyncCard.vue'
import RecordsEmptyState from '../../components/records/RecordsEmptyState.vue'
import RouteOverviewCard from '../../components/records/RouteOverviewCard.vue'
import { buildDemoCheckinProgress, selectPoseChallenge } from '../../mocks/checkin-success'
import { guideDemoData } from '../../mocks/guide'
import { buildCheckinOverview, recordsDemoData } from '../../mocks/records'
import {
  addVideoDemoCheckin,
  mergeVideoDemoCheckinRecords,
  mergeVideoDemoRecordSources,
} from '../../state/video-demo'
import type { CheckinSuccessData, PoseType } from '../../types/checkin-success'
import type { GuideSpot } from '../../types/guide'
import type {
  CheckinStatsData,
  CheckinTab,
  RecordsViewStatus,
  ResolvedCheckinRecord,
} from '../../types/records'

const activeTab = ref<CheckinTab>('checked')
const pageStatus = ref<RecordsViewStatus>(recordsDemoData.initialStatus)
const checkinSuccessData = ref<CheckinSuccessData | null>(null)
const isDemoCheckinOpening = ref(false)
const isCheckinSuccessModalVisible = ref(false)

// 开发时可改为某个 PoseType 固定姿势；默认 undefined 使用随机姿势。
const FIXED_DEMO_POSE: PoseType | undefined = undefined

const statusBarHeight = uni.getSystemInfoSync().statusBarHeight ?? 20
let navigationBarHeight = 44

try {
  const menuButton = uni.getMenuButtonBoundingClientRect()
  const menuTopGap = menuButton.top - statusBarHeight
  if (menuButton.height > 0 && menuTopGap >= 0) {
    navigationBarHeight = menuButton.height + menuTopGap * 2
  }
} catch {
  navigationBarHeight = 44
}

const headerStyle = {
  paddingTop: `${statusBarHeight}px`,
}

const navigationStyle = {
  height: `${navigationBarHeight}px`,
}

const spotById = computed(() => {
  const mapping = new Map<string, GuideSpot>()
  guideDemoData.spots.forEach((spot) => mapping.set(spot.id, spot))
  return mapping
})

const resolvedRecords = computed<ResolvedCheckinRecord[]>(() => {
  const result: ResolvedCheckinRecord[] = []

  mergeVideoDemoCheckinRecords(recordsDemoData.records).forEach((record) => {
    const spot = spotById.value.get(record.spotId)
    if (!spot) return
    result.push({ record, spot })
  })

  return result
})

const checkinOverview = computed(() =>
  buildCheckinOverview(mergeVideoDemoRecordSources(recordsDemoData.records), guideDemoData.spots),
)

const checkedSpotIds = computed(() => new Set(checkinOverview.value.checkedSpotIds))

const checkedRecordsNewestFirst = computed(() =>
  [...resolvedRecords.value].sort(
    (left, right) => Date.parse(right.record.checkedAt) - Date.parse(left.record.checkedAt),
  ),
)

const uncheckedSpots = computed(() =>
  guideDemoData.spots.filter((spot) => !checkedSpotIds.value.has(spot.id)),
)

const checkinSuccessSpot = computed(() => {
  const data = checkinSuccessData.value
  return data ? spotById.value.get(data.spotId) ?? null : null
})

const routeRecords = computed(() => {
  return [...resolvedRecords.value]
    .sort((left, right) => Date.parse(left.record.checkedAt) - Date.parse(right.record.checkedAt))
})

const stats = computed<CheckinStatsData>(() => {
  return {
    checkedCount: checkinOverview.value.checkedCount,
    totalCount: checkinOverview.value.totalCount,
    progressRatio: checkinOverview.value.progressRatio,
    progressPercentage: checkinOverview.value.progressPercentage,
  }
})

function handleBack() {
  uni.navigateBack()
}

function handleTabSelect(tab: CheckinTab) {
  activeTab.value = tab
}

function openSpotDetail(spotId: string) {
  uni.navigateTo({
    url: `/pages/spot-detail/index?spotId=${encodeURIComponent(spotId)}`,
  })
}

function goToGuide() {
  uni.navigateTo({
    url: '/pages/guide/index',
  })
}

function showRoutePlaceholder() {
  uni.showToast({
    title: '路线详情开发中',
    icon: 'none',
  })
}

function retryLocalDemo() {
  pageStatus.value = 'ready'
  uni.showToast({
    title: '已恢复本地演示数据',
    icon: 'none',
  })
}

function formatCurrentTimeLabel(now: Date) {
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `今天 ${hours}:${minutes}`
}

function handleDemoCheckin() {
  if (isDemoCheckinOpening.value) {
    return
  }

  isDemoCheckinOpening.value = true
  try {
    const demoSpot = uncheckedSpots.value.find((spot) => spot.id === 'bugao-mountain')
      ?? uncheckedSpots.value[0]
    if (!demoSpot) {
      uni.showToast({
        title: '暂无未打卡点位可演示',
        icon: 'none',
      })
      return
    }

    const now = new Date()
    const checkedAt = now.toISOString()
    const pose = selectPoseChallenge(Math.random(), FIXED_DEMO_POSE)
    const demoProgress = buildDemoCheckinProgress(
      mergeVideoDemoRecordSources(recordsDemoData.records),
      guideDemoData.spots,
      demoSpot.id,
    )

    checkinSuccessData.value = {
      recordId: `demo-checkin-success-${demoSpot.id}-${now.getTime()}`,
      spotId: demoSpot.id,
      checkedAt,
      checkedAtLabel: formatCurrentTimeLabel(now),
      checkinMethod: 'video-demo',
      methodLabel: '点位打卡 · 演示',
      checkedCount: demoProgress.checkedCount,
      totalCount: demoProgress.totalCount,
      photoRequired: true,
      poseChallengeId: pose.id,
      pose,
      isDemo: true,
    }
    addVideoDemoCheckin({
      recordId: checkinSuccessData.value.recordId,
      spotId: demoSpot.id,
      checkedAt,
      checkedAtLabel: checkinSuccessData.value.checkedAtLabel,
      poseId: pose.id,
      methodLabel: '点位打卡 · 演示',
      isDemo: true,
    })
    isCheckinSuccessModalVisible.value = true
  } catch {
    uni.showToast({
      title: '演示打卡暂时无法打开',
      icon: 'none',
    })
  } finally {
    isDemoCheckinOpening.value = false
  }
}

function closeDemoCheckin() {
  isCheckinSuccessModalVisible.value = false
  checkinSuccessData.value = null
  isDemoCheckinOpening.value = false
}

function handleStartPhoto(data: CheckinSuccessData) {
  isCheckinSuccessModalVisible.value = false
  uni.navigateTo({
    url: `/pages/materials/index?spotId=${encodeURIComponent(data.spotId)}&poseId=${encodeURIComponent(data.pose.id)}`,
  })
}

function handleViewCheckinSpot(spotId: string) {
  openSpotDetail(spotId)
}
</script>

<template>
  <view class="records-page">
    <view class="records-header" :style="headerStyle">
      <view class="records-header__bar" :style="navigationStyle">
        <view class="records-header__back" hover-class="records-header__back--pressed" @tap="handleBack">
          <image src="/static/guide/icon-back.svg" alt="返回" mode="aspectFit" />
        </view>
        <text class="records-header__title">我的打卡</text>
      </view>
    </view>

    <scroll-view class="records-page__scroll" scroll-y enable-back-to-top>
      <view class="records-page__content">
        <view v-if="pageStatus === 'loading'" class="records-loading" aria-label="正在加载演示数据">
          <view class="records-loading__stats">
            <view v-for="index in 3" :key="index" class="records-loading__stat" />
          </view>
          <view class="records-loading__sync" />
          <view class="records-loading__tabs" />
          <view v-for="index in 3" :key="`card-${index}`" class="records-loading__card" />
        </view>

        <RecordsEmptyState
          v-else-if="pageStatus === 'error'"
          title="打卡数据暂时无法加载"
          description="当前仅恢复本地演示数据，不会请求后端"
          action-label="重新加载"
          @action="retryLocalDemo"
        />

        <template v-else>
          <CheckinStats :stats="stats" />

          <view class="records-page__sync">
            <ProductSyncCard :product="recordsDemoData.product" />
          </view>

          <view class="demo-checkin-card">
            <view class="demo-checkin-copy">
              <view class="demo-checkin-heading">
                <text class="demo-checkin-title">前端演示</text>
                <text class="demo-checkin-badge">演示</text>
              </view>
              <text class="demo-checkin-desc">
                模拟完成一次新的校园点位打卡
              </text>
            </view>
            <button
              class="demo-checkin-button"
              :disabled="isDemoCheckinOpening"
              @tap="handleDemoCheckin"
            >
              演示新打卡
            </button>
          </view>

          <view class="records-page__tabs">
            <CheckinStatusTabs
              :active-tab="activeTab"
              :checked-count="stats.checkedCount"
              :unchecked-count="uncheckedSpots.length"
              @select="handleTabSelect"
            />
          </view>

          <view class="records-page__list">
            <template v-if="activeTab === 'checked'">
              <CheckinRecordCard
                v-for="entry in checkedRecordsNewestFirst"
                :key="entry.record.id"
                mode="checked"
                :spot="entry.spot"
                :record="entry.record"
                @view-details="openSpotDetail"
              />
              <RecordsEmptyState
                v-if="checkedRecordsNewestFirst.length === 0"
                title="还没有打卡记录"
                description="完成一次打卡后将在这里显示"
              />
            </template>

            <template v-else>
              <CheckinRecordCard
                v-for="spot in uncheckedSpots"
                :key="spot.id"
                mode="unchecked"
                :spot="spot"
                @view-details="openSpotDetail"
                @go-guide="goToGuide"
              />
              <RecordsEmptyState
                v-if="uncheckedSpots.length === 0"
                title="已完成全部点位"
              />
            </template>
          </view>

          <view class="records-page__route">
            <RouteOverviewCard
              :records="routeRecords"
              :total-count="stats.totalCount"
              @view-route="showRoutePlaceholder"
            />
          </view>
        </template>
      </view>
    </scroll-view>

    <CheckinSuccessModal
      v-if="isCheckinSuccessModalVisible && checkinSuccessData && checkinSuccessSpot"
      :checkin-data="checkinSuccessData"
      :spot="checkinSuccessSpot"
      @close="closeDemoCheckin"
      @dismiss="closeDemoCheckin"
      @start-photo="handleStartPhoto"
      @view-spot="handleViewCheckinSpot"
    />
  </view>
</template>

<style scoped>
.records-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
  flex-direction: column;
  background: #fbf7f2;
  color: #22211f;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.records-header {
  position: relative;
  z-index: 10;
  flex: none;
  background: #fbf7f2;
}

.records-header__bar {
  position: relative;
  display: flex;
  min-height: 88rpx;
  align-items: center;
  justify-content: center;
}

.records-header__back {
  position: absolute;
  left: 18rpx;
  display: flex;
  width: 70rpx;
  height: 70rpx;
  align-items: center;
  justify-content: center;
}

.records-header__back image {
  width: 54rpx;
  height: 54rpx;
}

.records-header__back--pressed {
  opacity: 0.62;
}

.records-header__title {
  color: #1f1f1f;
  font-size: 40rpx;
  font-weight: 700;
  line-height: 60rpx;
}

.records-page__scroll {
  min-height: 0;
  flex: 1;
}

.records-page__content {
  box-sizing: border-box;
  padding: 24rpx 48rpx calc(48rpx + env(safe-area-inset-bottom));
}

.records-page__sync {
  margin-top: 26rpx;
}

.demo-checkin-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  width: 100%;
  min-height: 94rpx;
  gap: 20rpx;
  margin-top: 18rpx;
  padding: 18rpx 20rpx;
  border: 2rpx dashed #c7dcd5;
  border-radius: 20rpx;
  background: #f5fbf8;
}

.demo-checkin-copy {
  min-width: 0;
  flex: 1;
}

.demo-checkin-heading {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.demo-checkin-title,
.demo-checkin-desc {
  display: block;
}

.demo-checkin-title {
  color: #2f8f77;
  font-size: 22rpx;
  font-weight: 700;
  line-height: 32rpx;
}

.demo-checkin-badge {
  flex: none;
  padding: 2rpx 10rpx;
  border-radius: 999rpx;
  background: #e1f1eb;
  color: #287d67;
  font-size: 18rpx;
  font-weight: 700;
  line-height: 28rpx;
  white-space: nowrap;
}

.demo-checkin-desc {
  margin-top: 2rpx;
  color: #7b817e;
  font-size: 20rpx;
  line-height: 31rpx;
}

.demo-checkin-button {
  display: flex;
  height: 58rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  padding: 0 22rpx;
  border: 2rpx solid #43ae91;
  border-radius: 30rpx;
  background: #ffffff;
  color: #287d67;
  font-size: 22rpx;
  font-weight: 700;
  line-height: 58rpx;
  opacity: 1;
  white-space: nowrap;
}

.demo-checkin-button::after {
  border: 0;
}

.demo-checkin-button[disabled] {
  background: #edf4f1;
  color: #8aa69d;
  opacity: 0.62;
}

.records-page__tabs {
  margin-top: 40rpx;
}

.records-page__list {
  display: flex;
  flex-direction: column;
  gap: 38rpx;
  margin-top: 38rpx;
}

.records-page__route {
  margin-top: 46rpx;
}

.records-loading__stats {
  display: flex;
  gap: 28rpx;
}

.records-loading__stat,
.records-loading__sync,
.records-loading__tabs,
.records-loading__card {
  border-radius: 22rpx;
  background: linear-gradient(100deg, #f0ebe5 25%, #faf7f3 45%, #f0ebe5 65%);
  background-size: 220% 100%;
  animation: records-loading-pulse 1.5s ease-in-out infinite;
}

.records-loading__stat {
  height: 170rpx;
  flex: 1;
}

.records-loading__sync {
  height: 125rpx;
  margin-top: 26rpx;
}

.records-loading__tabs {
  height: 97rpx;
  margin-top: 40rpx;
  border-radius: 50rpx;
}

.records-loading__card {
  height: 272rpx;
  margin-top: 38rpx;
}

@keyframes records-loading-pulse {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
</style>
