<script setup lang="ts">
import type { GuideSpot } from '../../types/guide'

defineProps<{ spots: readonly GuideSpot[] }>()
const emit = defineEmits<{ viewSpot: [spotId: string] }>()
</script>

<template>
  <swiper class="result-gallery" circular :indicator-dots="spots.length > 1" indicator-color="rgba(255,255,255,.55)" indicator-active-color="#ffffff">
    <swiper-item v-for="spot in spots" :key="spot.id">
      <view class="result-gallery__slide" @tap="emit('viewSpot', spot.id)">
        <image :src="spot.coverImage" :alt="spot.name" mode="aspectFill" />
        <view class="result-gallery__shade" />
        <text>{{ spot.name }}</text>
      </view>
    </swiper-item>
  </swiper>
</template>

<style scoped>
.result-gallery { width: 100%; height: 390rpx; overflow: hidden; border-radius: 30rpx; background: #e9e4dc; }
.result-gallery__slide { position: relative; width: 100%; height: 100%; overflow: hidden; }
.result-gallery image { width: 100%; height: 100%; }
.result-gallery__shade { position: absolute; inset: 0; background: linear-gradient(transparent 55%, rgba(18, 33, 27, .62)); }
.result-gallery text { position: absolute; right: 28rpx; bottom: 28rpx; left: 28rpx; color: #fff; font-size: 31rpx; font-weight: 800; }
</style>
