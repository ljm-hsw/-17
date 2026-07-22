<script setup lang="ts">
import type { GuideCategory, GuideCategoryId } from '../../types/guide'

defineProps<{
  categories: readonly GuideCategory[]
  activeId: GuideCategoryId
}>()

defineEmits<{
  select: [id: GuideCategoryId]
}>()
</script>

<template>
  <scroll-view class="guide-tabs" scroll-x :show-scrollbar="false">
    <view class="guide-tabs__track">
      <view
        v-for="category in categories"
        :key="category.id"
        class="guide-tabs__item"
        :class="{ 'guide-tabs__item--active': category.id === activeId }"
        hover-class="guide-tabs__item--pressed"
        @tap="$emit('select', category.id)"
      >
        <text>{{ category.label }}</text>
      </view>
    </view>
  </scroll-view>
</template>

<style scoped>
.guide-tabs {
  width: 100%;
  height: 71rpx;
  white-space: nowrap;
}

.guide-tabs__track {
  display: inline-flex;
  height: 71rpx;
  align-items: center;
  gap: 9rpx;
  padding: 0 18rpx;
}

.guide-tabs__item {
  display: flex;
  height: 56rpx;
  align-items: center;
  justify-content: center;
  padding: 0 22rpx;
  border-radius: 29rpx;
  color: #595651;
  font-size: 25rpx;
  font-weight: 500;
}

.guide-tabs__item--active {
  background: #49aa96;
  color: #ffffff;
  font-weight: 700;
}

.guide-tabs__item--pressed {
  opacity: 0.72;
}
</style>
