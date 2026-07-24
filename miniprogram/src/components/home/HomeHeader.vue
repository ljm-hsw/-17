<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import type { HomeBrand } from '../../types/home'

defineProps<{
  brand: HomeBrand
}>()

interface MenuButtonRect {
  top: number
}

const headerTop = ref(12)

const headerStyle = computed(() => ({
  paddingTop: `${headerTop.value}px`,
}))

onMounted(() => {
  const windowInfo = uni.getWindowInfo()
  const statusBarHeight = windowInfo.statusBarHeight ?? 20
  const menuButtonApi = (
    uni as typeof uni & {
      getMenuButtonBoundingClientRect?: () => MenuButtonRect
    }
  ).getMenuButtonBoundingClientRect
  const menuButtonRect = menuButtonApi?.()

  headerTop.value = menuButtonRect
    ? Math.max(statusBarHeight + 8, menuButtonRect.top - 6)
    : statusBarHeight + 12
})
</script>

<template>
  <view class="home-header" :style="headerStyle">
    <view class="home-header__content">
      <image
        class="home-header__logo"
        :src="brand.logo"
        :alt="brand.title"
        mode="aspectFill"
      />
      <view class="home-header__copy">
        <text class="home-header__title">{{ brand.title }}</text>
        <text class="home-header__subtitle">{{ brand.subtitle }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.home-header {
  box-sizing: border-box;
  padding-right: 44rpx;
  padding-left: 75rpx;
}

.home-header__content {
  display: flex;
  align-items: flex-start;
  height: 118rpx;
}

.home-header__logo {
  flex: none;
  width: 118rpx;
  height: 118rpx;
  overflow: hidden;
  border-radius: 50%;
}

.home-header__copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  margin-left: 11rpx;
}

.home-header__title {
  color: #171816;
  font-size: 59rpx;
  font-weight: 700;
  line-height: 76rpx;
  white-space: nowrap;
}

.home-header__subtitle {
  color: #77746e;
  font-size: 22rpx;
  font-weight: 500;
  line-height: 42rpx;
  white-space: nowrap;
}
</style>
