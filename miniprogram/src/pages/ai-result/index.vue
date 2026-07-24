<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import AiResultContent from '../../components/ai-result/AiResultContent.vue'
import AiResultGallery from '../../components/ai-result/AiResultGallery.vue'
import AiResultHeader from '../../components/ai-result/AiResultHeader.vue'
import { aiGenerationDemoData, buildAiGenerationResult, buildJourneySpots, parseAiGenerationOptions } from '../../mocks/ai-generation'
import { guideDemoData } from '../../mocks/guide'
import { recordsDemoData } from '../../mocks/records'
import { mergeVideoDemoCheckinRecords } from '../../state/video-demo'
import type { AiGenerationOptions } from '../../types/ai-generation'

const generationOptions = ref<AiGenerationOptions>(parseAiGenerationOptions())
const journeySpots = computed(() => buildJourneySpots(
  mergeVideoDemoCheckinRecords(recordsDemoData.records),
  guideDemoData.spots,
))
const result = computed(() => buildAiGenerationResult(journeySpots.value, generationOptions.value.style))

onLoad((query) => { generationOptions.value = parseAiGenerationOptions(query) })

function handleBack() {
  if (getCurrentPages().length > 1) uni.navigateBack()
  else uni.reLaunch({ url: '/pages/ai-chat/index' })
}

function viewSpot(spotId: string) {
  uni.navigateTo({ url: `/pages/spot-detail/index?spotId=${encodeURIComponent(spotId)}` })
}

function copyText(content: string) {
  uni.setClipboardData({ data: content, success: () => uni.showToast({ title: '文案已复制', icon: 'none' }) })
}

function regenerate() {
  uni.redirectTo({
    url: `/pages/ai-generating/index?generationType=${generationOptions.value.generationType}&source=video-demo&style=${generationOptions.value.style}`,
  })
}

function returnToAi() { uni.reLaunch({ url: '/pages/ai-chat/index' }) }
function showSharePlaceholder() { uni.showToast({ title: '分享功能待接入', icon: 'none' }) }
</script>

<template>
  <view class="result-page">
    <AiResultHeader @back="handleBack" />
    <scroll-view class="result-page__scroll" scroll-y :show-scrollbar="false">
      <view class="result-page__content">
        <text class="result-page__badge">{{ aiGenerationDemoData.resultBadge }}</text>
        <AiResultGallery :spots="journeySpots" @view-spot="viewSpot" />
        <AiResultContent :result="result" :route-names="journeySpots.map((spot) => spot.name)" @copy="copyText" />
        <view class="result-page__actions">
          <button class="result-page__primary" @tap="regenerate">重新编织</button>
          <button @tap="showSharePlaceholder">分享</button>
          <button @tap="returnToAi">返回AI智能体</button>
        </view>
        <text class="result-page__notice">内容为固定前端演示文本，未调用真实智能体，也未保存或发布。</text>
      </view>
    </scroll-view>
  </view>
</template>

<style scoped>
.result-page { display: flex; width: 100%; height: 100vh; overflow: hidden; flex-direction: column; background: #fbf7f1; color: #2c332f; }
.result-page__scroll { min-height: 0; flex: 1; }
.result-page__content { display: flex; box-sizing: border-box; padding: 22rpx 32rpx calc(48rpx + env(safe-area-inset-bottom)); gap: 26rpx; flex-direction: column; }
.result-page__badge { align-self: flex-start; padding: 7rpx 17rpx; border-radius: 22rpx; background: #edf7f2; color: #3d826d; font-size: 21rpx; font-weight: 700; }
.result-page__actions { display: grid; gap: 16rpx; grid-template-columns: 1fr 1fr; }
.result-page__actions button { height: 76rpx; margin: 0; border: 2rpx solid #d7d0c7; border-radius: 38rpx; background: #fff; color: #56605b; font-size: 24rpx; font-weight: 700; line-height: 74rpx; }
.result-page__actions button::after { border: 0; }
.result-page__actions .result-page__primary { border-color: #319071; background: #319071; color: #fff; }
.result-page__actions button:last-child { grid-column: 1 / -1; }
.result-page__notice { color: #999187; font-size: 21rpx; line-height: 34rpx; text-align: center; }
</style>
