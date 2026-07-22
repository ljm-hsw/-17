<script setup lang="ts">
import type { ProfileServiceId, ProfileServiceItem } from '../../types/profile'

defineProps<{
  items: readonly ProfileServiceItem[]
}>()

defineEmits<{
  select: [id: ProfileServiceId]
}>()
</script>

<template>
  <view class="profile-menu">
    <text class="profile-menu__title">服务与帮助</text>
    <view class="profile-menu__list">
      <view
        v-for="(item, index) in items"
        :key="item.id"
        class="profile-menu__row"
        :class="{ 'profile-menu__row--divided': index > 0 }"
        hover-class="profile-menu__row--pressed"
        @tap="$emit('select', item.id)"
      >
        <view class="profile-menu__icon"><text>{{ item.iconText }}</text></view>
        <text class="profile-menu__row-title">{{ item.title }}</text>
        <text class="profile-menu__arrow">›</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.profile-menu__title {
  display: block;
  color: #2d2b28;
  font-size: 32rpx;
  font-weight: 700;
  line-height: 48rpx;
}

.profile-menu__list {
  overflow: hidden;
  margin-top: 16rpx;
  border: 2rpx solid #f0e9e1;
  border-radius: 26rpx;
  background: #fffdfb;
  box-shadow: 0 8rpx 20rpx rgba(125, 105, 87, 0.08);
}

.profile-menu__row {
  position: relative;
  box-sizing: border-box;
  display: flex;
  height: 96rpx;
  align-items: center;
  padding: 0 28rpx 0 24rpx;
}

.profile-menu__row--divided::before {
  position: absolute;
  top: 0;
  right: 28rpx;
  left: 92rpx;
  height: 2rpx;
  background: #f0ebe5;
  content: "";
}

.profile-menu__row--pressed {
  background: #f7f3ed;
}

.profile-menu__icon {
  display: flex;
  width: 52rpx;
  height: 52rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e8f5ef;
  color: #318a73;
  font-size: 23rpx;
  font-weight: 700;
}

.profile-menu__row-title {
  min-width: 0;
  flex: 1;
  margin-left: 20rpx;
  color: #302e2b;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 42rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: keep-all;
  white-space: nowrap;
}

.profile-menu__arrow {
  flex: none;
  margin-left: 20rpx;
  color: #aaa198;
  font-size: 40rpx;
  font-weight: 300;
  line-height: 42rpx;
}
</style>
