<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ProfileUserDemo } from '../../types/profile'

const props = defineProps<{
  user: ProfileUserDemo
}>()

const avatarLoadFailed = ref(false)

watch(
  () => props.user.avatar,
  () => {
    avatarLoadFailed.value = false
  },
)
</script>

<template>
  <view class="profile-user-card">
    <view class="profile-user-card__avatar">
      <image
        v-if="!avatarLoadFailed"
        :src="user.avatar"
        alt="前端演示用户头像"
        mode="aspectFill"
        @error="avatarLoadFailed = true"
      />
      <text v-else>游</text>
    </view>

    <view class="profile-user-card__copy">
      <text class="profile-user-card__nickname">{{ user.nickname }}</text>
      <text class="profile-user-card__role">{{ user.roleLabel }}</text>
    </view>

    <view class="profile-user-card__demo-badge">
      <text>{{ user.demoLabel }}</text>
    </view>
  </view>
</template>

<style scoped>
.profile-user-card {
  display: flex;
  min-height: 146rpx;
  align-items: center;
  box-sizing: border-box;
  padding: 22rpx 28rpx;
  border-radius: 28rpx;
  background: #fffdfc;
  box-shadow: 0 4rpx 20rpx rgba(185, 175, 166, 0.08);
}

.profile-user-card__avatar {
  display: flex;
  width: 96rpx;
  height: 96rpx;
  overflow: hidden;
  flex: none;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #e9e2da;
  border-radius: 50%;
  background: #f3ece3;
  color: #5b8f7f;
  font-size: 32rpx;
  font-weight: 700;
}

.profile-user-card__avatar image {
  width: 100%;
  height: 100%;
}

.profile-user-card__copy {
  display: flex;
  min-width: 0;
  flex: 1;
  margin-left: 24rpx;
  flex-direction: column;
}

.profile-user-card__nickname,
.profile-user-card__role {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-user-card__nickname {
  color: #2b2926;
  font-size: 32rpx;
  font-weight: 700;
  line-height: 48rpx;
}

.profile-user-card__role {
  margin-top: 2rpx;
  color: #8d857e;
  font-size: 24rpx;
  line-height: 36rpx;
}

.profile-user-card__demo-badge {
  display: flex;
  min-height: 58rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  margin-left: 16rpx;
  padding: 0 20rpx;
  border: 2rpx solid #daeee7;
  border-radius: 30rpx;
  background: #eff8f4;
  color: #398e78;
  font-size: 22rpx;
  font-weight: 600;
  white-space: nowrap;
}
</style>
