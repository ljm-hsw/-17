<script setup lang="ts">
import { computed } from 'vue'
import HomeTabBar from '../../components/home/HomeTabBar.vue'
import ProfileBindingCard from '../../components/profile/ProfileBindingCard.vue'
import ProfileDigitalCards from '../../components/profile/ProfileDigitalCards.vue'
import ProfileHeader from '../../components/profile/ProfileHeader.vue'
import ProfileMenuList from '../../components/profile/ProfileMenuList.vue'
import ProfileStatsCard from '../../components/profile/ProfileStatsCard.vue'
import { bindingDemoData } from '../../mocks/binding'
import { guideDemoData } from '../../mocks/guide'
import { homeDemoData } from '../../mocks/home'
import { buildProfileStats, profileDemoData } from '../../mocks/profile'
import { recordsDemoData } from '../../mocks/records'
import { mergeVideoDemoRecordSources } from '../../state/video-demo'
import type { HomeNavigationId } from '../../types/home'
import type { ProfileServiceId } from '../../types/profile'

const profileStats = computed(() => buildProfileStats(
  mergeVideoDemoRecordSources(recordsDemoData.records),
  guideDemoData.spots,
))
const bindingStatus = bindingDemoData.initialStatus
const productCode = bindingStatus === 'bound'
  ? bindingDemoData.product.productCode
  : undefined

function openPage(url: string) {
  uni.navigateTo({
    url,
    fail: () => {
      uni.showToast({
        title: '页面打开失败，请重试',
        icon: 'none',
      })
    },
  })
}

function handleServiceSelect(id: ProfileServiceId) {
  if (id === 'feedback') {
    uni.showToast({
      title: '意见提交功能待接入',
      icon: 'none',
    })
    return
  }

  uni.showModal({
    title: '关于设备',
    content: '游迹织梦当前使用文创产品与点位打卡装置完成校园互动体验。页面中的产品状态、编号及使用记录均为本地前端演示数据，暂未接入实时设备状态。',
    showCancel: false,
    confirmText: '我知道了',
    confirmColor: '#318A73',
  })
}

function handleNavigationSelect(id: HomeNavigationId) {
  if (id === 'profile') return
  if (id === 'home') {
    uni.reLaunch({
      url: '/pages/index/index',
    })
    return
  }
  uni.reLaunch({
    url: '/pages/ai-chat/index',
  })
}
</script>

<template>
  <view class="profile-page">
    <ProfileHeader />

    <scroll-view
      class="profile-page__scroll"
      scroll-y
      enable-back-to-top
      :show-scrollbar="false"
    >
      <view class="profile-page__content">
        <ProfileBindingCard
          :status="bindingStatus"
          :product-code="productCode"
          @open="openPage('/pages/binding/index')"
        />

        <ProfileStatsCard :stats="profileStats" />

        <ProfileDigitalCards
          :stats="profileStats"
          @open="openPage('/pages/records/index')"
        />

        <ProfileMenuList
          :items="profileDemoData.serviceItems"
          @select="handleServiceSelect"
        />

        <text class="profile-page__demo-note">
          当前用户资料、统计和产品状态均为本地前端演示
        </text>
      </view>
    </scroll-view>

    <HomeTabBar
      :items="homeDemoData.navigation"
      active-id="profile"
      @select="handleNavigationSelect"
    />
  </view>
</template>

<style scoped>
.profile-page {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  flex-direction: column;
  background: #fbf7f2;
  color: #2d2b28;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.profile-page__scroll {
  min-height: 0;
  flex: 1;
}

.profile-page__content {
  display: flex;
  box-sizing: border-box;
  padding: 22rpx 28rpx calc(189rpx + env(safe-area-inset-bottom) + 40rpx);
  gap: 24rpx;
  flex-direction: column;
}

.profile-page__demo-note {
  display: block;
  padding: 4rpx 28rpx 12rpx;
  color: #a49b91;
  font-size: 21rpx;
  line-height: 34rpx;
  text-align: center;
}
</style>
