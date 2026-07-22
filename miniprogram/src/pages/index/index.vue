<script setup lang="ts">
import { computed } from 'vue'
import HomeFeatureGrid from '../../components/home/HomeFeatureGrid.vue'
import HomeHeader from '../../components/home/HomeHeader.vue'
import HomeScenery from '../../components/home/HomeScenery.vue'
import HomeTabBar from '../../components/home/HomeTabBar.vue'
import VisitProgress from '../../components/home/VisitProgress.vue'
import { guideDemoData } from '../../mocks/guide'
import { homeDemoData } from '../../mocks/home'
import { buildCheckinOverview, recordsDemoData } from '../../mocks/records'
import { mergeVideoDemoRecordSources } from '../../state/video-demo'
import type {
  HomeFeatureId,
  HomeNavigationId,
  HomeProduct,
  HomeProgress,
} from '../../types/home'

let lastSceneryOpenAt = 0

const homeProgress = computed<HomeProgress>(() => {
  const checkinOverview = buildCheckinOverview(
    mergeVideoDemoRecordSources(recordsDemoData.records),
    guideDemoData.spots,
  )
  return {
    visitedCount: checkinOverview.checkedCount,
    totalCount: checkinOverview.totalCount,
  }
})

const homeProduct = computed<HomeProduct>(() => ({
  label: homeDemoData.productPresentation.label,
  code: recordsDemoData.product.productCode,
  status: recordsDemoData.product.bindingStatus === 'bound' ? '已绑定' : '未绑定',
  editIcon: homeDemoData.productPresentation.editIcon,
}))

function showComingSoon() {
  uni.showToast({
    title: '功能开发中',
    icon: 'none',
  })
}

function openBindingPage() {
  uni.navigateTo({ url: '/pages/binding/index' })
}

function handleFeatureSelect(id: HomeFeatureId) {
  if (id === 'guide') {
    uni.navigateTo({
      url: '/pages/guide/index',
    })
    return
  }

  if (id === 'records') {
    uni.navigateTo({
      url: '/pages/records/index',
    })
    return
  }

  if (id === 'binding') {
    openBindingPage()
    return
  }

  if (id === 'materials') {
    uni.navigateTo({
      url: '/pages/materials/index',
    })
    return
  }

  if (id === 'recommend') {
    uni.navigateTo({
      url: '/pages/recommendations/index',
    })
    return
  }

  showComingSoon()
}

function handleNavigationSelect(id: HomeNavigationId) {
  if (id === 'home') return
  if (id === 'ai') {
    uni.reLaunch({
      url: '/pages/ai-chat/index',
    })
    return
  }
  if (id === 'profile') {
    uni.reLaunch({
      url: '/pages/profile/index',
    })
    return
  }
  showComingSoon()
}

function openScenerySpot(spotId: string) {
  const now = Date.now()
  if (now - lastSceneryOpenAt < 800) return
  lastSceneryOpenAt = now
  uni.navigateTo({
    url: `/pages/spot-detail/index?spotId=${encodeURIComponent(spotId)}`,
    fail: () => {
      lastSceneryOpenAt = 0
      uni.showToast({
        title: '点位详情暂时无法打开',
        icon: 'none',
      })
    },
  })
}
</script>

<template>
  <view class="home-page">
    <HomeHeader :brand="homeDemoData.brand" />
    <scroll-view
      class="home-page__scroll"
      scroll-y
      enable-back-to-top
      :show-scrollbar="false"
    >
      <view class="home-page__content">
        <image
          class="home-page__hero"
          :src="homeDemoData.heroImage"
          :alt="homeDemoData.heroAlt"
          mode="aspectFill"
        />

        <view class="home-page__progress">
          <VisitProgress
            :progress="homeProgress"
            :product="homeProduct"
            @edit="openBindingPage"
          />
        </view>

        <HomeFeatureGrid :features="homeDemoData.features" @select="handleFeatureSelect" />
        <HomeScenery :spots="guideDemoData.spots" @select="openScenerySpot" />
      </view>
    </scroll-view>
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
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  flex-direction: column;
  padding-top: 16rpx;
  background: #fff9f1;
  color: #171816;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.home-page__scroll {
  width: 100%;
  height: 0;
  min-height: 0;
  flex: 1;
}

.home-page__content {
  box-sizing: border-box;
  width: 100%;
  overflow-x: hidden;
  padding-bottom: calc(189rpx + env(safe-area-inset-bottom) + 56rpx);
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
