<script setup lang="ts">
import type { HomeNavigationId, HomeNavigationItem } from '../../types/home'

defineProps<{
  items: readonly HomeNavigationItem[]
  activeId: HomeNavigationId
}>()

defineEmits<{
  select: [id: HomeNavigationId]
}>()
</script>

<template>
  <view class="home-tab-bar">
    <view class="home-tab-bar__separator" />
    <view class="home-tab-bar__items">
      <view
        v-for="item in items"
        :key="item.id"
        class="home-tab-bar__item"
        hover-class="home-tab-bar__item--pressed"
        @tap="$emit('select', item.id)"
      >
        <image
          class="home-tab-bar__icon"
          :src="item.icon"
          :alt="item.label"
          mode="aspectFit"
        />
        <text
          class="home-tab-bar__label"
          :class="{ 'home-tab-bar__label--active': item.id === activeId }"
        >
          {{ item.label }}
        </text>
        <view v-if="item.id === activeId" class="home-tab-bar__active-mark" />
      </view>
    </view>
  </view>
</template>

<style scoped>
.home-tab-bar {
  position: fixed;
  z-index: 20;
  right: 0;
  bottom: 0;
  left: 0;
  box-sizing: border-box;
  padding-bottom: env(safe-area-inset-bottom);
  background: #fff9f1;
}

.home-tab-bar__separator {
  height: 2rpx;
  margin: 0 44rpx;
  background: #efe8de;
}

.home-tab-bar__items {
  display: flex;
  align-items: stretch;
  justify-content: space-around;
  height: 189rpx;
}

.home-tab-bar__item {
  position: relative;
  display: flex;
  width: 206rpx;
  align-items: center;
  flex-direction: column;
  padding-top: 24rpx;
}

.home-tab-bar__item--pressed {
  opacity: 0.65;
}

.home-tab-bar__icon {
  width: 61rpx;
  height: 61rpx;
}

.home-tab-bar__label {
  margin-top: 9rpx;
  color: #171816;
  font-size: 26rpx;
  font-weight: 500;
  line-height: 48rpx;
}

.home-tab-bar__label--active {
  color: #278c79;
  font-weight: 700;
}

.home-tab-bar__active-mark {
  width: 22rpx;
  height: 7rpx;
  margin-top: 2rpx;
  border-radius: 4rpx;
  background: #48a995;
}
</style>
