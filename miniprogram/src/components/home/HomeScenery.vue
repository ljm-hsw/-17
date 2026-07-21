<script setup lang="ts">
import { ref } from 'vue'

import type { HomeSceneryItem } from '../../types/home'

defineProps<{
  items: readonly HomeSceneryItem[]
}>()

const currentIndex = ref(0)

function handleChange(event: { detail: { current: number } }) {
  currentIndex.value = event.detail.current
}
</script>

<template>
  <view class="home-scenery">
    <text class="home-scenery__title">校园风光</text>
    <swiper
      class="home-scenery__swiper"
      circular
      next-margin="342rpx"
      :current="currentIndex"
      @change="handleChange"
    >
      <swiper-item v-for="item in items" :key="item.id" class="home-scenery__slide">
        <image
          class="home-scenery__image"
          :src="item.image"
          :alt="item.title"
          mode="aspectFill"
        />
      </swiper-item>
    </swiper>
    <view v-if="items.length > 1" class="home-scenery__dots">
      <view
        v-for="(item, index) in items"
        :key="item.id"
        class="home-scenery__dot"
        :class="{ 'home-scenery__dot--active': index === currentIndex }"
      />
    </view>
  </view>
</template>

<style scoped>
.home-scenery {
  margin: 42rpx 44rpx 0;
}

.home-scenery__title {
  display: block;
  color: #171816;
  font-size: 39rpx;
  font-weight: 700;
  line-height: 77rpx;
}

.home-scenery__swiper {
  width: 100%;
  height: 276rpx;
}

.home-scenery__slide {
  overflow: visible;
}

.home-scenery__image {
  display: block;
  width: 276rpx;
  height: 276rpx;
}

.home-scenery__dots {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48rpx;
  gap: 24rpx;
}

.home-scenery__dot {
  width: 15rpx;
  height: 15rpx;
  border-radius: 8rpx;
  background: #c9c2b9;
}

.home-scenery__dot--active {
  background: #77746e;
}
</style>
