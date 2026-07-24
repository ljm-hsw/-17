<script setup lang="ts">
import type { GuideRouteSpotItem } from '../../types/guide'

defineProps<{ items: readonly GuideRouteSpotItem[] }>()

const emit = defineEmits<{
  viewSpot: [spotId: string]
  addSpots: []
}>()
</script>

<template>
  <view class="route-overview">
    <view class="route-overview__intro">
      <text class="route-overview__title">我的路线点位</text>
      <text class="route-overview__notice">由已打卡点位和手动加入的点位组成</text>
    </view>

    <view v-if="items.length" class="route-overview__list">
      <view v-for="item in items" :key="item.spot.id" class="route-overview__card">
        <view class="route-overview__heading">
          <view class="route-overview__name-wrap">
            <text class="route-overview__name">{{ item.spot.name }}</text>
            <text
              class="route-overview__status"
              :class="{ 'route-overview__status--checked': item.isCheckedIn }"
            >
              {{ item.isCheckedIn ? '已打卡' : '已加入路线' }}
            </text>
          </view>
          <view class="route-overview__button" @tap="emit('viewSpot', item.spot.id)">
            查看点位
          </view>
        </view>
        <text class="route-overview__meta">
          {{ item.categoryLabel }}<template v-if="item.spot.tags[0]"> · {{ item.spot.tags[0] }}</template>
        </text>
        <text class="route-overview__summary">{{ item.spot.summary }}</text>
      </view>
    </view>

    <view v-else class="route-overview__empty">
      <text class="route-overview__empty-title">暂未添加路线点位</text>
      <text class="route-overview__empty-desc">可前往推荐点位页面选择想去的校园景点</text>
      <view
        class="route-overview__empty-button"
        hover-class="route-overview__empty-button--pressed"
        @tap="emit('addSpots')"
      >
        去添加点位
      </view>
    </view>
  </view>
</template>

<style scoped>
.route-overview {
  box-sizing: border-box;
  width: calc(100% - 56rpx);
  margin: 0 auto;
  padding: 30rpx 28rpx 18rpx;
  border-radius: 32rpx;
  background: #fffefb;
  box-shadow: 0 10rpx 24rpx rgba(115, 97, 77, 0.1);
}

.route-overview__intro {
  padding-bottom: 24rpx;
  border-bottom: 2rpx solid #f0ebe4;
}

.route-overview__title,
.route-overview__notice,
.route-overview__card text,
.route-overview__empty text {
  display: block;
}

.route-overview__title {
  color: #274e42;
  font-size: 31rpx;
  font-weight: 800;
}

.route-overview__notice {
  margin-top: 7rpx;
  color: #7b756e;
  font-size: 22rpx;
  line-height: 34rpx;
}

.route-overview__list {
  margin-top: 8rpx;
}

.route-overview__card {
  padding: 24rpx 0;
  border-bottom: 2rpx solid #f2eee8;
}

.route-overview__card:last-child {
  border-bottom: 0;
}

.route-overview__heading,
.route-overview__name-wrap {
  display: flex;
  align-items: flex-start;
}

.route-overview__heading {
  justify-content: space-between;
  gap: 14rpx;
}

.route-overview__name-wrap {
  min-width: 0;
  flex-wrap: wrap;
  gap: 10rpx;
}

.route-overview__name {
  color: #272b28;
  font-size: 29rpx;
  font-weight: 800;
  line-height: 42rpx;
  word-break: keep-all;
}

.route-overview__status {
  flex: none;
  padding: 4rpx 12rpx;
  border-radius: 18rpx;
  background: #eef3f0;
  color: #55766c;
  font-size: 19rpx;
  font-weight: 700;
  white-space: nowrap;
}

.route-overview__status--checked {
  background: #e4f4ee;
  color: #278c79;
}

.route-overview__button {
  flex: none;
  padding: 8rpx 15rpx;
  border: 2rpx solid #b9d9cf;
  border-radius: 24rpx;
  color: #347766;
  font-size: 21rpx;
  font-weight: 700;
  white-space: nowrap;
}

.route-overview__meta {
  margin-top: 8rpx;
  color: #8a8279;
  font-size: 22rpx;
  line-height: 34rpx;
}

.route-overview__summary {
  display: -webkit-box !important;
  overflow: hidden;
  margin-top: 9rpx;
  color: #66645f;
  font-size: 23rpx;
  line-height: 37rpx;
  word-break: break-word;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.route-overview__empty {
  display: flex;
  align-items: center;
  padding: 44rpx 20rpx 34rpx;
  flex-direction: column;
  text-align: center;
}

.route-overview__empty-title {
  color: #354d46;
  font-size: 28rpx;
  font-weight: 700;
}

.route-overview__empty-desc {
  margin-top: 10rpx;
  color: #8a8279;
  font-size: 22rpx;
  line-height: 34rpx;
}

.route-overview__empty-button {
  display: flex;
  height: 64rpx;
  align-items: center;
  justify-content: center;
  margin-top: 24rpx;
  padding: 0 30rpx;
  border-radius: 32rpx;
  background: #e6f3ef;
  color: #277c6b;
  font-size: 23rpx;
  font-weight: 700;
}

.route-overview__empty-button--pressed {
  opacity: 0.7;
}
</style>
