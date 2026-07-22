<script setup lang="ts">
import { computed, ref } from 'vue'
import CampusMap from '../../components/guide/CampusMap.vue'
import GuideCategoryTabs from '../../components/guide/GuideCategoryTabs.vue'
import GuideSearchBar from '../../components/guide/GuideSearchBar.vue'
import RouteSummaryCard from '../../components/guide/RouteSummaryCard.vue'
import SpotInfoModal from '../../components/guide/SpotInfoModal.vue'
import HomeTabBar from '../../components/home/HomeTabBar.vue'
import { guideDemoData } from '../../mocks/guide'
import { homeDemoData } from '../../mocks/home'
import type {
  GuideCategoryId,
  GuideMapCoordinate,
  GuideMapViewState,
  GuideSpot,
  SpotDistanceState,
} from '../../types/guide'
import type { HomeNavigationId } from '../../types/home'

const ENABLE_MAP_CALIBRATION = false

const query = ref('')
const activeCategoryId = ref<GuideCategoryId>('all')
const selectedSpotId = ref<string | null>(null)
const joinedRouteSpotIds = ref<readonly string[]>(
  guideDemoData.spots.filter((spot) => spot.isInRoute).map((spot) => spot.id),
)
const currentMapScale = ref<number>(guideDemoData.initialMapScale)
const currentMapCenter = ref<GuideMapCoordinate>({ ...guideDemoData.mapCenter })
const calibrationIndex = ref(0)
const calibrationSelectorVisible = ref(false)
const calibrationCoordinates = ref<Record<string, GuideMapCoordinate>>({})
const completedCalibrationIds = ref<readonly string[]>([])
const spotDistanceState: SpotDistanceState = {
  status: 'unavailable',
  label: '开启定位后查看',
}

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

const normalizedQuery = computed(() => query.value.trim().toLocaleLowerCase())

const filteredSpots = computed(() =>
  guideDemoData.spots.filter((spot) => {
    const matchesCategory =
      activeCategoryId.value === 'all' || spot.category === activeCategoryId.value
    const matchesQuery =
      normalizedQuery.value.length === 0 ||
      spot.name.toLocaleLowerCase().includes(normalizedQuery.value)
    return matchesCategory && matchesQuery
  }),
)

const displaySpots = computed(() =>
  filteredSpots.value.map((spot) => {
    const calibrated = calibrationCoordinates.value[spot.id]
    return calibrated ? { ...spot, ...calibrated } : spot
  }),
)

const currentCalibrationSpot = computed(() => guideDemoData.spots[calibrationIndex.value])

const currentCalibrationCoordinate = computed(() => {
  const spot = currentCalibrationSpot.value
  return calibrationCoordinates.value[spot.id] ?? {
    latitude: spot.latitude,
    longitude: spot.longitude,
  }
})

const currentCalibrationCompleted = computed(() =>
  completedCalibrationIds.value.includes(currentCalibrationSpot.value.id),
)

const selectedSpot = computed(
  () => guideDemoData.spots.find((spot) => spot.id === selectedSpotId.value) ?? null,
)

const selectedSpotIsInRoute = computed(
  () => selectedSpot.value !== null && joinedRouteSpotIds.value.includes(selectedSpot.value.id),
)

function handleBack() {
  uni.navigateBack()
}

function handleCategorySelect(id: GuideCategoryId) {
  activeCategoryId.value = id
  closeSpotModal()
}

function openSpotModal(spot: GuideSpot) {
  selectedSpotId.value = spot.id
}

function closeSpotModal() {
  selectedSpotId.value = null
}

function handleMapRegionChange(state: GuideMapViewState) {
  currentMapScale.value = state.scale
  currentMapCenter.value = {
    latitude: state.latitude,
    longitude: state.longitude,
  }
}

function handleMapReset() {
  closeSpotModal()
}

function openCalibrationSelector() {
  if (!ENABLE_MAP_CALIBRATION) return
  calibrationSelectorVisible.value = true
}

function closeCalibrationSelector() {
  calibrationSelectorVisible.value = false
}

function selectCalibrationSpot(index: number) {
  calibrationIndex.value = index
  query.value = ''
  activeCategoryId.value = 'all'
  closeSpotModal()
  closeCalibrationSelector()
}

function selectPreviousCalibrationSpot() {
  calibrationIndex.value =
    (calibrationIndex.value - 1 + guideDemoData.spots.length) % guideDemoData.spots.length
}

function selectNextCalibrationSpot() {
  calibrationIndex.value = (calibrationIndex.value + 1) % guideDemoData.spots.length
}

function buildCalibratedCoordinateList() {
  return guideDemoData.spots.map((spot) => {
    const coordinate = calibrationCoordinates.value[spot.id] ?? {
      latitude: spot.latitude,
      longitude: spot.longitude,
    }
    return {
      markerId: spot.markerId,
      name: spot.name,
      latitude: coordinate.latitude,
      longitude: coordinate.longitude,
    }
  })
}

function printCompleteCalibrationArray() {
  const output = buildCalibratedCoordinateList()
    .map(
      (spot) =>
        `  { markerId: ${spot.markerId}, name: '${spot.name}', latitude: ${spot.latitude.toFixed(6)}, longitude: ${spot.longitude.toFixed(6)} },`,
    )
    .join('\n')
  console.log(`export const guideSpots = [\n${output}\n]`)
}

function completeCurrentCalibrationSpot() {
  const spot = currentCalibrationSpot.value
  if (!calibrationCoordinates.value[spot.id]) {
    uni.showToast({
      title: '请先点击地图校准位置',
      icon: 'none',
    })
    return
  }

  if (!completedCalibrationIds.value.includes(spot.id)) {
    completedCalibrationIds.value = [...completedCalibrationIds.value, spot.id]
  }

  if (completedCalibrationIds.value.length === guideDemoData.spots.length) {
    printCompleteCalibrationArray()
    uni.showToast({
      title: '全部点位已校准并输出',
      icon: 'none',
    })
    return
  }

  selectNextCalibrationSpot()
}

function handleMapCalibrationTap(coordinate: GuideMapCoordinate | null) {
  if (!ENABLE_MAP_CALIBRATION) return

  if (!coordinate) {
    uni.showToast({
      title: '当前基础库未返回坐标',
      icon: 'none',
    })
    return
  }

  const spot = currentCalibrationSpot.value
  calibrationCoordinates.value = {
    ...calibrationCoordinates.value,
    [spot.id]: coordinate,
  }

  const coordinateOutput = {
    markerId: spot.markerId,
    name: spot.name,
    latitude: Number(coordinate.latitude.toFixed(6)),
    longitude: Number(coordinate.longitude.toFixed(6)),
  }
  console.log(coordinateOutput)

  const coordinateText = `当前点位：${spot.name}\n纬度：${coordinate.latitude.toFixed(6)}\n经度：${coordinate.longitude.toFixed(6)}`
  uni.showModal({
    title: '地图坐标校准',
    content: coordinateText,
    confirmText: '复制坐标',
    success: (result) => {
      if (!result.confirm) return
      uni.setClipboardData({
        data: coordinateText,
      })
    },
  })
}

function showSpotDetailsPlaceholder() {
  uni.showToast({
    title: '点位详情开发中',
    icon: 'none',
  })
}

function toggleRouteSpot(spot: GuideSpot) {
  const alreadyJoined = joinedRouteSpotIds.value.includes(spot.id)
  joinedRouteSpotIds.value = alreadyJoined
    ? joinedRouteSpotIds.value.filter((id) => id !== spot.id)
    : [...joinedRouteSpotIds.value, spot.id]

  uni.showToast({
    title: alreadyJoined ? '已移出路线' : '已加入路线',
    icon: 'none',
  })
}

function showRoutePlaceholder() {
  uni.showToast({
    title: '路线详情开发中',
    icon: 'none',
  })
}

function handleNavigationSelect(id: HomeNavigationId) {
  if (id === 'home') {
    uni.reLaunch({ url: '/pages/index/index' })
    return
  }

  uni.showToast({
    title: '功能开发中',
    icon: 'none',
  })
}
</script>

<template>
  <view class="guide-page">
    <view class="guide-header" :style="headerStyle">
      <view class="guide-header__bar" :style="navigationStyle">
        <view
          class="guide-header__back"
          hover-class="guide-header__back--pressed"
          @tap="handleBack"
        >
          <image src="/static/guide/icon-back.svg" alt="返回" mode="aspectFit" />
        </view>
        <text class="guide-header__title">校园导览</text>
      </view>
    </view>

    <GuideSearchBar v-model="query" :placeholder="guideDemoData.searchPlaceholder" />
    <GuideCategoryTabs
      :categories="guideDemoData.categories"
      :active-id="activeCategoryId"
      @select="handleCategorySelect"
    />
    <CampusMap
      class="guide-page__map"
      :spots="displaySpots"
      :selected-spot-id="selectedSpotId"
      :map-center="guideDemoData.mapCenter"
      :initial-scale="guideDemoData.initialMapScale"
      :min-scale="guideDemoData.mapMinScale"
      :max-scale="guideDemoData.mapMaxScale"
      :preview-image="guideDemoData.mapImage"
      :interaction-disabled="selectedSpot !== null || calibrationSelectorVisible"
      :calibration-enabled="ENABLE_MAP_CALIBRATION"
      @select-spot="openSpotModal"
      @region-change="handleMapRegionChange"
      @map-tap="handleMapCalibrationTap"
      @open-calibration="openCalibrationSelector"
      @reset="handleMapReset"
    />
    <view v-if="filteredSpots.length === 0" class="guide-page__empty">
      <text>未找到相关点位</text>
    </view>

    <view v-if="ENABLE_MAP_CALIBRATION" class="guide-calibration-panel">
      <view class="guide-calibration-panel__heading">
        <text class="guide-calibration-panel__title">
          当前校准：{{ currentCalibrationSpot.name }}
        </text>
        <text class="guide-calibration-panel__count">
          {{ completedCalibrationIds.length }}/{{ guideDemoData.spots.length }}
        </text>
      </view>
      <text class="guide-calibration-panel__tip">请点击地图中的真实位置</text>
      <view class="guide-calibration-panel__coordinate">
        <text>纬度：{{ currentCalibrationCoordinate.latitude.toFixed(6) }}</text>
        <text>经度：{{ currentCalibrationCoordinate.longitude.toFixed(6) }}</text>
      </view>
      <view class="guide-calibration-panel__actions">
        <view class="guide-calibration-panel__button" @tap="selectPreviousCalibrationSpot">
          <text>上一个点位</text>
        </view>
        <view class="guide-calibration-panel__button" @tap="selectNextCalibrationSpot">
          <text>下一个点位</text>
        </view>
        <view
          class="guide-calibration-panel__button guide-calibration-panel__button--primary"
          :class="{ 'guide-calibration-panel__button--done': currentCalibrationCompleted }"
          @tap="completeCurrentCalibrationSpot"
        >
          <text>{{ currentCalibrationCompleted ? '本点位已完成' : '完成本点位' }}</text>
        </view>
      </view>
    </view>

    <view
      v-if="ENABLE_MAP_CALIBRATION && calibrationSelectorVisible"
      class="guide-calibration-selector"
      @tap="closeCalibrationSelector"
    >
      <view class="guide-calibration-selector__card" @tap.stop>
        <view class="guide-calibration-selector__heading">
          <text>选择校准点位</text>
          <text class="guide-calibration-selector__close" @tap="closeCalibrationSelector">×</text>
        </view>
        <scroll-view class="guide-calibration-selector__list" scroll-y>
          <view
            v-for="(spot, index) in guideDemoData.spots"
            :key="spot.id"
            class="guide-calibration-selector__item"
            :class="{
              'guide-calibration-selector__item--active': index === calibrationIndex,
            }"
            @tap="selectCalibrationSpot(index)"
          >
            <text>{{ spot.markerId }}. {{ spot.name }}</text>
            <text v-if="completedCalibrationIds.includes(spot.id)" class="guide-calibration-selector__done">
              已完成
            </text>
          </view>
        </scroll-view>
      </view>
    </view>
    <view class="guide-page__route">
      <RouteSummaryCard :route="guideDemoData.route" @view-route="showRoutePlaceholder" />
    </view>

    <HomeTabBar
      :items="homeDemoData.navigation"
      active-id="home"
      @select="handleNavigationSelect"
    />

    <SpotInfoModal
      v-if="selectedSpot"
      :spot="selectedSpot"
      :is-in-route="selectedSpotIsInRoute"
      :distance-state="spotDistanceState"
      @close="closeSpotModal"
      @view-details="showSpotDetailsPlaceholder"
      @toggle-route="toggleRouteSpot"
    />
  </view>
</template>

<style scoped>
.guide-page {
  box-sizing: border-box;
  display: flex;
  height: 100vh;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: calc(245rpx + env(safe-area-inset-bottom));
  background: #fff9f1;
  color: #171816;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.guide-page__map {
  flex: 1;
  min-height: 0;
}

.guide-page__empty {
  position: absolute;
  z-index: 8;
  top: calc(320rpx + env(safe-area-inset-top));
  left: 50%;
  padding: 15rpx 27rpx;
  border-radius: 25rpx;
  background: rgba(255, 254, 251, 0.94);
  box-shadow: 0 5rpx 16rpx rgba(77, 71, 63, 0.13);
  color: #6d675f;
  font-size: 25rpx;
  font-weight: 600;
  transform: translateX(-50%);
}

.guide-page__route {
  position: relative;
  z-index: 10;
  flex: none;
  padding: 20rpx 0 24rpx;
  background: #fff9f1;
}

.guide-calibration-panel {
  position: relative;
  z-index: 12;
  box-sizing: border-box;
  flex: none;
  padding: 18rpx 28rpx 20rpx;
  border-top: 2rpx solid #dcebe6;
  background: #f2faf7;
}

.guide-calibration-panel__heading,
.guide-calibration-panel__coordinate,
.guide-calibration-panel__actions,
.guide-calibration-selector__heading,
.guide-calibration-selector__item {
  display: flex;
  align-items: center;
}

.guide-calibration-panel__heading {
  justify-content: space-between;
}

.guide-calibration-panel__title {
  color: #276f61;
  font-size: 27rpx;
  font-weight: 700;
}

.guide-calibration-panel__count,
.guide-calibration-panel__tip {
  color: #6f7d78;
  font-size: 22rpx;
}

.guide-calibration-panel__tip {
  display: block;
  margin-top: 5rpx;
}

.guide-calibration-panel__coordinate {
  justify-content: space-between;
  margin-top: 10rpx;
  color: #4d5c57;
  font-size: 22rpx;
  font-family: Consolas, monospace;
}

.guide-calibration-panel__actions {
  gap: 12rpx;
  margin-top: 14rpx;
}

.guide-calibration-panel__button {
  display: flex;
  height: 56rpx;
  align-items: center;
  justify-content: center;
  padding: 0 18rpx;
  border: 2rpx solid #bdd8cf;
  border-radius: 28rpx;
  color: #46625a;
  font-size: 22rpx;
  font-weight: 600;
}

.guide-calibration-panel__button--primary {
  flex: 1;
  border-color: #277c6b;
  background: #277c6b;
  color: #ffffff;
}

.guide-calibration-panel__button--done {
  border-color: #e88b3a;
  background: #e88b3a;
}

.guide-calibration-selector {
  position: fixed;
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 50rpx;
  background: rgba(29, 33, 30, 0.44);
  inset: 0;
}

.guide-calibration-selector__card {
  box-sizing: border-box;
  width: 650rpx;
  padding: 30rpx;
  border-radius: 34rpx;
  background: #fffefc;
  box-shadow: 0 14rpx 40rpx rgba(77, 71, 63, 0.24);
}

.guide-calibration-selector__heading {
  justify-content: space-between;
  color: #171816;
  font-size: 32rpx;
  font-weight: 700;
}

.guide-calibration-selector__close {
  color: #77746e;
  font-size: 46rpx;
  font-weight: 400;
}

.guide-calibration-selector__list {
  height: 650rpx;
  margin-top: 20rpx;
}

.guide-calibration-selector__item {
  box-sizing: border-box;
  justify-content: space-between;
  height: 72rpx;
  padding: 0 22rpx;
  border-bottom: 2rpx solid #f0ebe4;
  color: #4d4944;
  font-size: 26rpx;
}

.guide-calibration-selector__item--active {
  border-radius: 18rpx;
  background: #e7f5f0;
  color: #277c6b;
  font-weight: 700;
}

.guide-calibration-selector__done {
  color: #e88b3a;
  font-size: 22rpx;
}

.guide-header {
  box-sizing: border-box;
  background: #fff9f1;
}

.guide-header__bar {
  position: relative;
  display: flex;
  min-height: 88rpx;
  align-items: center;
  justify-content: center;
}

.guide-header__back {
  position: absolute;
  left: 18rpx;
  display: flex;
  width: 70rpx;
  height: 70rpx;
  align-items: center;
  justify-content: center;
}

.guide-header__back image {
  width: 54rpx;
  height: 54rpx;
}

.guide-header__back--pressed {
  opacity: 0.62;
}

.guide-header__title {
  color: #171816;
  font-size: 41rpx;
  font-weight: 700;
  line-height: 64rpx;
}
</style>
