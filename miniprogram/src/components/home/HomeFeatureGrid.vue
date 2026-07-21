<script setup lang="ts">
import type { HomeFeature, HomeFeatureId } from '../../types/home'

defineProps<{
  features: readonly HomeFeature[]
}>()

defineEmits<{
  select: [id: HomeFeatureId]
}>()
</script>

<template>
  <view class="feature-grid">
    <view
      v-for="feature in features"
      :key="feature.id"
      class="feature-card"
      hover-class="feature-card--pressed"
      @tap="$emit('select', feature.id)"
    >
      <view class="feature-card__copy">
        <text class="feature-card__title">{{ feature.title }}</text>
        <view class="feature-card__description">
          <text v-for="line in feature.description" :key="line" class="feature-card__line">
            {{ line }}
          </text>
        </view>
      </view>
      <image
        class="feature-card__image"
        :class="`feature-card__image--${feature.id}`"
        :src="feature.image"
        :alt="feature.title"
        mode="aspectFit"
      />
    </view>
  </view>
</template>

<style scoped>
.feature-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 24rpx 18rpx;
  margin: 20rpx 44rpx 0;
}

.feature-card {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 322rpx;
  height: 243rpx;
  overflow: hidden;
  padding: 31rpx 18rpx 31rpx 26rpx;
  border: 2rpx solid #f1eae1;
  border-radius: 29rpx;
  background: #fffdfa;
  box-shadow: 0 7rpx 9rpx rgba(140, 119, 102, 0.08);
}

.feature-card--pressed {
  opacity: 0.78;
  transform: scale(0.98);
}

.feature-card__copy {
  display: flex;
  align-self: stretch;
  flex-direction: column;
  min-width: 135rpx;
}

.feature-card__title {
  color: #171816;
  font-size: 37rpx;
  font-weight: 700;
  line-height: 59rpx;
  white-space: nowrap;
}

.feature-card__description {
  display: flex;
  flex-direction: column;
  margin-top: 7rpx;
}

.feature-card__line {
  color: #77746e;
  font-size: 24rpx;
  font-weight: 500;
  line-height: 42rpx;
  white-space: nowrap;
}

.feature-card__image {
  flex: none;
  width: 125rpx;
  height: 125rpx;
}

.feature-card__image--guide {
  width: 123rpx;
  height: 123rpx;
}

.feature-card__image--binding {
  width: 123rpx;
  height: 108rpx;
}
</style>
