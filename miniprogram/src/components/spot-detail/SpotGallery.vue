<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { SpotGalleryChangeEvent } from '../../types/spot-detail'

const props = defineProps<{
  images: readonly string[]
  spotName: string
}>()

const currentIndex = ref(0)
const failedImages = ref<readonly string[]>([])

const hasMultipleImages = computed(() => props.images.length > 1)
const currentImage = computed(() => props.images[currentIndex.value] ?? props.images[0] ?? '')
const previewImages = computed(() =>
  props.images.filter((imagePath) => !failedImages.value.includes(imagePath)),
)

watch(
  () => props.images,
  () => {
    currentIndex.value = 0
    failedImages.value = []
  },
)

function handleChange(event: SpotGalleryChangeEvent) {
  currentIndex.value = event.detail.current
}

function handleImageError(imagePath: string) {
  if (!failedImages.value.includes(imagePath)) {
    failedImages.value = [...failedImages.value, imagePath]
  }
}

function previewCurrentImage() {
  if (!currentImage.value || failedImages.value.includes(currentImage.value)) return
  if (previewImages.value.length === 0) return

  uni.previewImage({
    current: currentImage.value,
    urls: [...previewImages.value],
    fail: () => {
      uni.showToast({
        title: '图片预览暂不可用',
        icon: 'none',
      })
    },
  })
}
</script>

<template>
  <view class="spot-gallery">
    <swiper
      v-if="images.length > 0"
      class="spot-gallery__swiper"
      :current="currentIndex"
      :circular="hasMultipleImages"
      @change="handleChange"
    >
      <swiper-item v-for="imagePath in images" :key="imagePath">
        <view class="spot-gallery__slide" @tap="previewCurrentImage">
          <image
            v-if="!failedImages.includes(imagePath)"
            class="spot-gallery__image"
            :src="imagePath"
            :alt="spotName"
            mode="aspectFill"
            @error="handleImageError(imagePath)"
          />
          <view v-else class="spot-gallery__placeholder">
            <text>图片暂不可用</text>
          </view>
        </view>
      </swiper-item>
    </swiper>

    <view v-else class="spot-gallery__placeholder spot-gallery__placeholder--empty">
      <text>图片暂不可用</text>
    </view>

    <view v-if="hasMultipleImages" class="spot-gallery__counter">
      <text>{{ currentIndex + 1 }}/{{ images.length }}</text>
    </view>
    <view v-if="hasMultipleImages" class="spot-gallery__dots">
      <view
        v-for="(_, index) in images"
        :key="index"
        class="spot-gallery__dot"
        :class="{ 'spot-gallery__dot--active': index === currentIndex }"
      />
    </view>
  </view>
</template>

<style scoped>
.spot-gallery {
  position: relative;
  width: 100%;
  height: 500rpx;
  overflow: hidden;
  border-radius: 0 0 30rpx 30rpx;
  background: #eee8e1;
}

.spot-gallery__swiper,
.spot-gallery__slide,
.spot-gallery__image,
.spot-gallery__placeholder {
  width: 100%;
  height: 100%;
}

.spot-gallery__slide,
.spot-gallery__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spot-gallery__placeholder {
  background: #ebe5de;
  color: #8b847c;
  font-size: 26rpx;
}

.spot-gallery__placeholder--empty {
  position: absolute;
  inset: 0;
}

.spot-gallery__counter {
  position: absolute;
  top: 30rpx;
  right: 30rpx;
  display: flex;
  min-width: 80rpx;
  height: 54rpx;
  align-items: center;
  justify-content: center;
  padding: 0 14rpx;
  border-radius: 29rpx;
  background: rgba(53, 67, 74, 0.72);
  color: #ffffff;
  font-size: 25rpx;
  font-weight: 600;
}

.spot-gallery__dots {
  position: absolute;
  right: 28rpx;
  bottom: 22rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 10rpx 14rpx;
  border-radius: 24rpx;
  background: rgba(56, 70, 75, 0.52);
}

.spot-gallery__dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.82);
}

.spot-gallery__dot--active {
  background: #d8e35f;
}
</style>
