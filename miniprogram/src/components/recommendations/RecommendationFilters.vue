<script setup lang="ts">
import type {
  RecommendationFilterId,
  RecommendationFilterOption,
} from '../../types/recommendations'

defineProps<{
  options: readonly RecommendationFilterOption[]
  activeId: RecommendationFilterId
}>()

const emit = defineEmits<{
  select: [id: RecommendationFilterId]
}>()
</script>

<template>
  <view class="recommendation-filters">
    <scroll-view class="recommendation-filters__scroll" scroll-x :show-scrollbar="false">
      <view class="recommendation-filters__list">
        <view
          v-for="option in options"
          :key="option.id"
          class="recommendation-filters__item"
          :class="{ 'recommendation-filters__item--active': option.id === activeId }"
          @tap="emit('select', option.id)"
        >
          <text>{{ option.label }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<style scoped>
.recommendation-filters {
  box-sizing: border-box;
  flex-shrink: 0;
  width: 100%;
  padding: 14rpx 0 18rpx;
  border-bottom: 1rpx solid rgba(48, 91, 77, 0.08);
  background: #fbf6f0;
}

.recommendation-filters__scroll {
  width: 100%;
  white-space: nowrap;
}

.recommendation-filters__list {
  display: inline-flex;
  gap: 14rpx;
  box-sizing: border-box;
  min-width: 100%;
  padding: 0 28rpx;
}

.recommendation-filters__item {
  flex: none;
  box-sizing: border-box;
  padding: 13rpx 24rpx;
  border: 1rpx solid #d9e4df;
  border-radius: 999rpx;
  background: #fffcf8;
  color: #587168;
  font-size: 25rpx;
  line-height: 1;
  white-space: nowrap;
}

.recommendation-filters__item--active {
  border-color: #45b297;
  background: #45b297;
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 7rpx 18rpx rgba(69, 178, 151, 0.2);
}
</style>
