<script setup lang="ts">
import { computed, ref } from 'vue'
import type { GuideSpot } from '../../types/guide'
import { chunkItems } from '../../utils/home-scenery'

const props = defineProps<{
  spots?: readonly GuideSpot[]
}>()

const emit = defineEmits<{
  select: [spotId: string]
}>()

const currentIndex = ref(0)
const failedSpotIds = ref<readonly string[]>([])
const availableSpots = computed<readonly GuideSpot[]>(() => props.spots ?? [])
const sceneryPages = computed(() => chunkItems(availableSpots.value, 2))
const totalPages = computed(() => sceneryPages.value.length)

function handleSceneryChange(event: { detail: { current: number } }) {
  currentIndex.value = event.detail.current
}

function handleImageError(spotId: string) {
  if (!failedSpotIds.value.includes(spotId)) {
    failedSpotIds.value = [...failedSpotIds.value, spotId]
  }
}

function imageFailed(spotId: string) {
  return failedSpotIds.value.includes(spotId)
}
</script>

<template>
  <view class="home-scenery">
    <view class="home-scenery__heading">
      <text class="home-scenery__title">校园风光</text>
      <text v-if="totalPages > 0" class="home-scenery__counter">
        {{ currentIndex + 1 }} / {{ totalPages }}
      </text>
    </view>
    <swiper
      v-if="totalPages > 0"
      class="home-scenery__swiper"
      autoplay
      circular
      :interval="2800"
      :duration="500"
      :current="currentIndex"
      @change="handleSceneryChange"
    >
      <swiper-item
        v-for="(page, pageIndex) in sceneryPages"
        :key="pageIndex"
        class="home-scenery__slide"
      >
        <view class="home-scenery__page">
          <view
            v-for="spot in page"
            :key="spot.id"
            class="home-scenery__card"
            hover-class="home-scenery__card--pressed"
            @tap="emit('select', spot.id)"
          >
            <image
              v-if="!imageFailed(spot.id)"
              class="home-scenery__image"
              :src="spot.coverImage"
              :alt="spot.name"
              mode="aspectFill"
              @error="handleImageError(spot.id)"
            />
            <view v-else class="home-scenery__placeholder">
              <text class="home-scenery__placeholder-name">{{ spot.name }}</text>
              <text>图片暂不可用</text>
            </view>
            <view class="home-scenery__shade" />
            <text class="home-scenery__name">{{ spot.name }}</text>
          </view>
        </view>
      </swiper-item>
    </swiper>
    <view v-else class="home-scenery__empty">
      <text>暂无校园风光</text>
    </view>
  </view>
</template>

<style scoped>
.home-scenery {
  margin: 42rpx 35rpx 0;
}

.home-scenery__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 9rpx;
}

.home-scenery__title {
  display: block;
  color: #171816;
  font-size: 39rpx;
  font-weight: 700;
  line-height: 77rpx;
}

.home-scenery__counter {
  color: #827c75;
  font-size: 23rpx;
  font-weight: 600;
  line-height: 36rpx;
  white-space: nowrap;
}

.home-scenery__swiper {
  width: 100%;
  height: 340rpx;
}

.home-scenery__slide {
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  padding: 0 9rpx 20rpx;
}

.home-scenery__page {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: stretch;
  gap: 18rpx;
}

.home-scenery__card {
  position: relative;
  box-sizing: border-box;
  width: calc((100% - 18rpx) / 2);
  height: 300rpx;
  overflow: hidden;
  border-radius: 22rpx;
  background: #edf3ef;
  box-shadow: 0 8rpx 18rpx rgba(113, 96, 80, 0.1);
}

.home-scenery__card--pressed {
  opacity: 0.76;
  transform: scale(0.985);
}

.home-scenery__image,
.home-scenery__placeholder {
  display: block;
  width: 100%;
  height: 100%;
}

.home-scenery__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background: linear-gradient(135deg, #f2eee6, #e5f2eb);
  color: #8a867f;
  font-size: 22rpx;
}

.home-scenery__placeholder-name {
  margin-bottom: 8rpx;
  color: #3d6f62;
  font-size: 25rpx;
  font-weight: 700;
}

.home-scenery__shade {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 92rpx;
  background: linear-gradient(transparent, rgba(25, 40, 34, 0.68));
}

.home-scenery__name {
  position: absolute;
  right: 18rpx;
  bottom: 15rpx;
  left: 18rpx;
  overflow: hidden;
  color: #ffffff;
  font-size: 25rpx;
  font-weight: 700;
  line-height: 38rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-break: keep-all;
}

.home-scenery__empty {
  box-sizing: border-box;
  display: flex;
  width: 100%;
  height: 220rpx;
  align-items: center;
  justify-content: center;
  border-radius: 22rpx;
  background: linear-gradient(135deg, #f8f2e9, #edf5f0);
  color: #807a72;
  font-size: 25rpx;
}
</style>
