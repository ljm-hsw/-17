<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import AiGeneratingHeader from '../../components/ai-generating/AiGeneratingHeader.vue'
import AiGenerationProgress from '../../components/ai-generating/AiGenerationProgress.vue'
import { aiGenerationDemoData, buildJourneySpots, parseAiGenerationOptions } from '../../mocks/ai-generation'
import { guideDemoData } from '../../mocks/guide'
import { recordsDemoData } from '../../mocks/records'
import { mergeVideoDemoCheckinRecords } from '../../state/video-demo'
import type { AiGenerationOptions } from '../../types/ai-generation'

const activeIndex = ref(0)
let options: AiGenerationOptions = parseAiGenerationOptions()
const timers: ReturnType<typeof setTimeout>[] = []
const journeySpots = computed(() => buildJourneySpots(
  mergeVideoDemoCheckinRecords(recordsDemoData.records),
  guideDemoData.spots,
))

onLoad((query) => {
  options = parseAiGenerationOptions(query)
  aiGenerationDemoData.steps.slice(1).forEach((_, index) => {
    timers.push(setTimeout(() => { activeIndex.value = index + 1 }, 420 * (index + 1)))
  })
  timers.push(setTimeout(() => {
    const style = encodeURIComponent(options.style)
    uni.redirectTo({
      url: `/pages/ai-result/index?generationType=${options.generationType}&source=${options.source}&style=${style}`,
    })
  }, aiGenerationDemoData.durationMs))
})

function handleBack() {
  if (getCurrentPages().length > 1) uni.navigateBack()
  else uni.reLaunch({ url: '/pages/ai-chat/index' })
}

onBeforeUnmount(() => timers.forEach((timer) => clearTimeout(timer)))
</script>

<template>
  <view class="generating-page">
    <AiGeneratingHeader @back="handleBack" />
    <view class="generating-page__content">
      <text class="generating-page__badge">{{ aiGenerationDemoData.badge }}</text>
      <view class="generating-page__hero">
        <view class="generating-page__weave"><text>游</text></view>
        <text class="generating-page__title">正在编织你的江安旅程</text>
        <text class="generating-page__subtitle">页面按照固定步骤演示内容流转，不会调用模型或后端</text>
        <text class="generating-page__route">{{ journeySpots.map((spot) => spot.name).join(' → ') }}</text>
      </view>
      <AiGenerationProgress :steps="aiGenerationDemoData.steps" :active-index="activeIndex" />
    </view>
  </view>
</template>

<style scoped>
.generating-page { width: 100%; min-height: 100vh; overflow: hidden; background: radial-gradient(circle at 80% 15%, #e0f4e9, transparent 32%), #fbf7f1; color: #26352f; }
.generating-page__content { display: flex; box-sizing: border-box; padding: 54rpx 40rpx calc(48rpx + env(safe-area-inset-bottom)); gap: 38rpx; flex-direction: column; }
.generating-page__badge { align-self: center; padding: 8rpx 18rpx; border-radius: 24rpx; background: #edf6f1; color: #40816d; font-size: 21rpx; font-weight: 700; }
.generating-page__hero { display: flex; align-items: center; flex-direction: column; text-align: center; }
.generating-page__weave { display: flex; width: 134rpx; height: 134rpx; align-items: center; justify-content: center; border-radius: 42rpx; background: linear-gradient(145deg, #3eaa87, #276f5a); color: #fff; box-shadow: 0 16rpx 36rpx rgba(55, 137, 111, .25); transform: rotate(-5deg); }
.generating-page__weave text { font-size: 54rpx; font-weight: 800; transform: rotate(5deg); }
.generating-page__title { margin-top: 32rpx; font-size: 38rpx; font-weight: 800; }
.generating-page__subtitle { max-width: 570rpx; margin-top: 14rpx; color: #7a7b76; font-size: 24rpx; line-height: 38rpx; }
.generating-page__route { margin-top: 18rpx; color: #357d66; font-size: 24rpx; font-weight: 700; line-height: 38rpx; }
</style>
