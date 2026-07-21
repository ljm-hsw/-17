<script setup lang="ts">
import HomeFeatureGrid from '../../components/home/HomeFeatureGrid.vue'
import HomeHeader from '../../components/home/HomeHeader.vue'
import HomeScenery from '../../components/home/HomeScenery.vue'
import HomeTabBar from '../../components/home/HomeTabBar.vue'
import VisitProgress from '../../components/home/VisitProgress.vue'
import { homeDemoData } from '../../mocks/home'
import type { HomeFeatureId, HomeNavigationId } from '../../types/home'

function showComingSoon() {
  uni.showToast({
    title: '功能开发中',
    icon: 'none',
  })
}

function handleFeatureSelect(_id: HomeFeatureId) {
  showComingSoon()
}

function handleNavigationSelect(id: HomeNavigationId) {
  if (id === 'home') return
  showComingSoon()
}
</script>

<template>
  <view class="home-page">
    <HomeHeader :brand="homeDemoData.brand" />

    <image
      class="home-page__hero"
      :src="homeDemoData.heroImage"
      :alt="homeDemoData.heroAlt"
      mode="aspectFill"
    />

    <view class="home-page__progress">
      <VisitProgress
        :progress="homeDemoData.progress"
        :product="homeDemoData.product"
        @edit="showComingSoon"
      />
    </view>

    <HomeFeatureGrid :features="homeDemoData.features" @select="handleFeatureSelect" />
    <HomeScenery :items="homeDemoData.scenery" />
    <HomeTabBar
      :items="homeDemoData.navigation"
      active-id="home"
      @select="handleNavigationSelect"
    />
  </view>
</template>

<style scoped>
.home-page {
  box-sizing: border-box;
  min-height: 100vh;
  padding-top: 16rpx;
  padding-bottom: calc(239rpx + env(safe-area-inset-bottom));
  background: #fff9f1;
  color: #171816;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.home-page__hero {
  display: block;
  width: 610rpx;
  height: 342rpx;
  margin: 72rpx auto 0;
}

.home-page__progress {
  margin-top: 79rpx;
}
</style>
