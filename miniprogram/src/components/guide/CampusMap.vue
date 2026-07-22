<script setup lang="ts">
import { computed, getCurrentInstance, nextTick, onMounted, ref } from 'vue'
import type {
  GuideMapCoordinate,
  GuideMapMarker,
  GuideMapPolyline,
  GuideMapViewState,
  GuideSpot,
} from '../../types/guide'

const props = defineProps<{
  spots: readonly GuideSpot[]
  selectedSpotId: string | null
  mapCenter: GuideMapCoordinate
  initialScale: number
  minScale: number
  maxScale: number
  previewImage: string
  interactionDisabled: boolean
  calibrationEnabled: boolean
}>()

const emit = defineEmits<{
  selectSpot: [spot: GuideSpot]
  regionChange: [state: GuideMapViewState]
  mapTap: [coordinate: GuideMapCoordinate | null]
  openCalibration: []
  reset: []
}>()

const componentInstance = getCurrentInstance()
let mapContext: UniNamespace.MapContext | null = null
let lastMarkerTapTime = 0

// 这些受控值只负责首次展示和用户主动复位；手势移动时不高频写回。
const controlledLatitude = ref(props.mapCenter.latitude)
const controlledLongitude = ref(props.mapCenter.longitude)
const controlledScale = ref(props.initialScale)

const currentCenter = ref<GuideMapCoordinate>({ ...props.mapCenter })
const currentScale = ref(props.initialScale)

const markerIdToSpot = computed(() => {
  const mapping = new Map<number, GuideSpot>()
  props.spots.forEach((spot) => mapping.set(spot.markerId, spot))
  return mapping
})

const visibleMarkers = computed<GuideMapMarker[]>(() =>
  props.spots.map((spot) => ({
    id: spot.markerId,
    latitude: spot.latitude,
    longitude: spot.longitude,
    iconPath: spot.iconPath,
    width: spot.id === props.selectedSpotId ? 24 : 22,
    height: spot.id === props.selectedSpotId ? 30 : 28,
    anchor: {
      x: 0.5,
      y: 1,
    },
    label: {
      content: spot.name,
      color: '#FFFFFF',
      fontSize: spot.id === props.selectedSpotId ? 14 : 13,
      borderRadius: 6,
      bgColor: spot.id === props.selectedSpotId ? '#E88B3A' : '#277C6B',
      padding: 5,
      textAlign: 'center',
      anchorX: spot.labelOffsetX,
      anchorY: spot.labelOffsetY,
    },
    zIndex: spot.id === props.selectedSpotId ? 10 : 1,
  })),
)

// 当前缺少经人工确认的道路折线，避免用直线冒充真实步行路线。
const routePolylines = computed<GuideMapPolyline[]>(() => [])

function getMapCenter(): Promise<GuideMapCoordinate> {
  return new Promise((resolve) => {
    if (!mapContext) {
      resolve(currentCenter.value)
      return
    }

    mapContext.getCenterLocation({
      success: (result) => {
        resolve({
          latitude: result.latitude,
          longitude: result.longitude,
        })
      },
      fail: () => resolve(currentCenter.value),
    })
  })
}

function getMapScale(): Promise<number> {
  return new Promise((resolve) => {
    if (!mapContext) {
      resolve(currentScale.value)
      return
    }

    mapContext.getScale({
      success: (result) => resolve(result.scale),
      fail: () => resolve(currentScale.value),
    })
  })
}

async function recordCurrentView() {
  const [center, scale] = await Promise.all([getMapCenter(), getMapScale()])
  currentCenter.value = center
  currentScale.value = scale
  emit('regionChange', {
    ...center,
    scale,
  })
}

function handleRegionChange(event: unknown) {
  const regionEvent = event as { detail?: { type?: string } }
  const phase = regionEvent.detail?.type
  if (phase && phase !== 'end') return
  void recordCurrentView()
}

function handleMarkerTap(event: unknown) {
  const markerEvent = event as { detail?: { markerId?: number | string } }
  const markerId = Number(markerEvent.detail?.markerId)
  const spot = markerIdToSpot.value.get(markerId)
  if (!spot) return

  lastMarkerTapTime = Date.now()
  emit('selectSpot', spot)
}

function handleMapTap(event: unknown) {
  if (Date.now() - lastMarkerTapTime < 350) return

  const mapEvent = event as {
    detail?: {
      latitude?: number
      longitude?: number
    }
  }
  const latitude = mapEvent.detail?.latitude
  const longitude = mapEvent.detail?.longitude

  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    emit('mapTap', null)
    return
  }

  emit('mapTap', {
    latitude: latitude as number,
    longitude: longitude as number,
  })
}

async function resetMap() {
  // 先同步至当前原生视野，再通过一次显式属性变化恢复演示中心与缩放。
  controlledLatitude.value = currentCenter.value.latitude
  controlledLongitude.value = currentCenter.value.longitude
  controlledScale.value = currentScale.value
  await nextTick()

  controlledLatitude.value = props.mapCenter.latitude
  controlledLongitude.value = props.mapCenter.longitude
  controlledScale.value = props.initialScale
  currentCenter.value = { ...props.mapCenter }
  currentScale.value = props.initialScale
  emit('regionChange', {
    ...props.mapCenter,
    scale: props.initialScale,
  })
  emit('reset')
}

function previewCampusMap() {
  uni.previewImage({
    current: props.previewImage,
    urls: [props.previewImage],
    fail: () => {
      uni.showToast({
        title: '全景图打开失败',
        icon: 'none',
      })
    },
  })
}

onMounted(() => {
  mapContext = uni.createMapContext('campus-map', componentInstance?.proxy)
})
</script>

<template>
  <view class="campus-map-shell">
    <map
      id="campus-map"
      class="campus-map"
      :latitude="controlledLatitude"
      :longitude="controlledLongitude"
      :scale="controlledScale"
      :min-scale="minScale"
      :max-scale="maxScale"
      :markers="visibleMarkers"
      :polyline="routePolylines"
      :enable-scroll="!interactionDisabled"
      :enable-zoom="!interactionDisabled"
      :enable-rotate="false"
      :enable-overlooking="false"
      :show-location="false"
      @markertap="handleMarkerTap"
      @regionchange="handleRegionChange"
      @tap="handleMapTap"
    />

    <cover-view class="campus-map-tools">
      <cover-view
        v-if="calibrationEnabled"
        class="campus-map-tools__button campus-map-tools__button--calibration"
        hover-class="campus-map-tools__button--pressed"
        @tap="$emit('openCalibration')"
      >
        校准点位
      </cover-view>
      <cover-view
        class="campus-map-tools__button"
        hover-class="campus-map-tools__button--pressed"
        @tap="resetMap"
      >
        复位地图
      </cover-view>
      <cover-view
        class="campus-map-tools__button campus-map-tools__button--wide"
        hover-class="campus-map-tools__button--pressed"
        @tap="previewCampusMap"
      >
        校园全景图
      </cover-view>
    </cover-view>
  </view>
</template>

<style scoped>
.campus-map-shell {
  position: relative;
  width: 750rpx;
  height: 100%;
  overflow: hidden;
  background: #edf0e7;
}

.campus-map {
  display: block;
  width: 750rpx;
  height: 100%;
}

.campus-map-tools {
  position: absolute;
  z-index: 8;
  top: 24rpx;
  right: 20rpx;
  display: flex;
  align-items: flex-end;
  flex-direction: column;
}

.campus-map-tools__button {
  box-sizing: border-box;
  min-width: 118rpx;
  height: 64rpx;
  padding: 0 18rpx;
  border: 2rpx solid rgba(221, 213, 202, 0.92);
  border-radius: 18rpx;
  background: rgba(255, 254, 251, 0.94);
  box-shadow: 0 6rpx 16rpx rgba(77, 71, 63, 0.15);
  color: #354d46;
  font-size: 23rpx;
  font-weight: 700;
  line-height: 64rpx;
  text-align: center;
}

.campus-map-tools__button--wide {
  min-width: 158rpx;
  margin-top: 12rpx;
}

.campus-map-tools__button--calibration {
  min-width: 142rpx;
  margin-bottom: 12rpx;
  background: rgba(39, 124, 107, 0.94);
  color: #ffffff;
}

.campus-map-tools__button--pressed {
  opacity: 0.7;
}
</style>
