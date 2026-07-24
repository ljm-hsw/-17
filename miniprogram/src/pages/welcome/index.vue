<script setup lang="ts">
import { ref } from 'vue'

import WelcomeBindingCard from '../../components/welcome/WelcomeBindingCard.vue'
import { welcomeDemoData } from '../../mocks/welcome'
import type { WelcomeAgreementType } from '../../types/welcome'

const agreed = ref(false)
const binding = ref(false)

function enterHome() {
  uni.reLaunch({
    url: '/pages/index/index',
  })
}

function toggleConsent() {
  agreed.value = !agreed.value
}

function handleMockBinding() {
  if (binding.value) return

  if (!agreed.value) {
    uni.showToast({
      title: '请先阅读并同意协议',
      icon: 'none',
    })
    return
  }

  binding.value = true
  uni.showToast({
    title: '演示绑定成功',
    icon: 'success',
    duration: 900,
  })

  setTimeout(enterHome, 900)
}

function handleBrowse() {
  if (binding.value) return
  enterHome()
}

function showAgreementPlaceholder(_type: WelcomeAgreementType) {
  uni.showToast({
    title: '内容准备中',
    icon: 'none',
  })
}
</script>

<template>
  <view class="welcome-page">
    <view class="welcome-page__glow welcome-page__glow--left" />
    <view class="welcome-page__glow welcome-page__glow--right" />
    <view class="welcome-page__glow welcome-page__glow--bottom" />

    <view class="welcome-page__content">
      <image
        class="welcome-page__hero"
        :src="welcomeDemoData.heroImage"
        :alt="welcomeDemoData.heroAlt"
        mode="aspectFill"
      />

      <WelcomeBindingCard
        class="welcome-page__binding-card"
        :data="welcomeDemoData"
        :agreed="agreed"
        :binding="binding"
        @toggle-consent="toggleConsent"
        @bind="handleMockBinding"
        @browse="handleBrowse"
        @agreement="showAgreementPlaceholder"
      />

      <view class="welcome-page__privacy">
        <image
          class="welcome-page__privacy-icon"
          :src="welcomeDemoData.privacyShieldIcon"
          alt="隐私保护"
          mode="aspectFit"
        />
        <text class="welcome-page__privacy-text">{{ welcomeDemoData.privacyNotice }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.welcome-page {
  position: relative;
  box-sizing: border-box;
  min-height: 100vh;
  overflow: hidden;
  padding-top: calc(var(--status-bar-height) + 12rpx);
  padding-bottom: calc(44rpx + env(safe-area-inset-bottom));
  background: linear-gradient(180deg, #fff7e7 0%, #fffdf5 100%);
  color: #171816;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.welcome-page__content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  flex-direction: column;
}

.welcome-page__hero {
  display: block;
  width: 715rpx;
  height: 664rpx;
  overflow: hidden;
  border-radius: 53rpx;
}

.welcome-page__binding-card {
  position: relative;
  z-index: 3;
  margin-top: -94rpx;
}

.welcome-page__privacy {
  display: flex;
  align-items: center;
  margin-top: 72rpx;
}

.welcome-page__privacy-icon {
  flex: none;
  width: 44rpx;
  height: 48rpx;
}

.welcome-page__privacy-text {
  margin-left: 15rpx;
  color: #5f5c57;
  font-size: 26rpx;
  font-weight: 400;
  line-height: 55rpx;
}

.welcome-page__glow {
  position: absolute;
  z-index: 1;
  border-radius: 50%;
  pointer-events: none;
}

.welcome-page__glow--left {
  bottom: 130rpx;
  left: -150rpx;
  width: 370rpx;
  height: 370rpx;
  background: rgba(255, 220, 161, 0.18);
  box-shadow: 0 0 100rpx 54rpx rgba(255, 220, 161, 0.1);
}

.welcome-page__glow--right {
  right: -110rpx;
  bottom: 360rpx;
  width: 329rpx;
  height: 329rpx;
  background: rgba(152, 214, 197, 0.14);
  box-shadow: 0 0 94rpx 50rpx rgba(152, 214, 197, 0.08);
}

.welcome-page__glow--bottom {
  right: -80rpx;
  bottom: -40rpx;
  width: 263rpx;
  height: 263rpx;
  background: rgba(255, 222, 169, 0.14);
  box-shadow: 0 0 90rpx 44rpx rgba(255, 222, 169, 0.08);
}
</style>
