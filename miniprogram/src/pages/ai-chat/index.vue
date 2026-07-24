<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'
import AiChatHeader from '../../components/ai-chat/AiChatHeader.vue'
import ChatComposer from '../../components/ai-chat/ChatComposer.vue'
import ChatMessageBubble from '../../components/ai-chat/ChatMessageBubble.vue'
import QuickQuestionList from '../../components/ai-chat/QuickQuestionList.vue'
import SpotRecommendationMessage from '../../components/ai-chat/SpotRecommendationMessage.vue'
import HomeTabBar from '../../components/home/HomeTabBar.vue'
import {
  AI_GENERATION_UNAVAILABLE_MESSAGE,
  USER_AVATAR_PATH,
  aiChatDemoData,
  buildRouteDemoReply,
  buildSpotDemoReply,
  createWelcomeMessages,
  findSpotIdInQuestion,
  inferQuestionType,
  isGenerationQuestionType,
} from '../../mocks/ai-chat'
import { guideDemoData } from '../../mocks/guide'
import { homeDemoData } from '../../mocks/home'
import { recordsDemoData } from '../../mocks/records'
import { mergeVideoDemoRecordSources } from '../../state/video-demo'
import type {
  AiQuestionType,
  ChatMessage,
  QuickQuestion,
} from '../../types/ai-chat'
import type { GuideSpot } from '../../types/guide'
import type { HomeNavigationId } from '../../types/home'

interface MessageRow {
  readonly message: ChatMessage
  readonly spot?: GuideSpot
}

const currentInput = ref('')
const keyboardHeight = ref(0)
const isGenerating = ref(false)
const messages = ref<ChatMessage[]>(createWelcomeMessages())
const scrollIntoView = ref('message-assistant-welcome')
const spotById = new Map<string, GuideSpot>(
  guideDemoData.spots.map((spot) => [spot.id, spot]),
)
const isKeyboardOpen = computed(() => keyboardHeight.value > 0)
const messageRows = computed<MessageRow[]>(() =>
  messages.value.map((message) => ({
    message,
    spot: message.spotId ? spotById.get(message.spotId) : undefined,
  })),
)

let messageSequence = 0
let replyTimer: ReturnType<typeof setTimeout> | undefined

function createMessageId(prefix: string) {
  messageSequence += 1
  return `${prefix}-${Date.now()}-${messageSequence}`
}

function formatTimeLabel() {
  const now = new Date()
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

async function scrollToMessage(messageId: string) {
  await nextTick()
  scrollIntoView.value = `message-${messageId}`
}

function appendMessage(message: ChatMessage) {
  messages.value.push(message)
  void scrollToMessage(message.id)
}

function replaceMessage(messageId: string, message: ChatMessage) {
  const index = messages.value.findIndex((item) => item.id === messageId)
  if (index < 0) {
    appendMessage(message)
    return
  }
  messages.value.splice(index, 1, message)
  void scrollToMessage(message.id)
}

function buildAssistantReply(type: AiQuestionType, question: string) {
  const spotId = findSpotIdInQuestion(question, guideDemoData.spots)

  if (type === 'spot' && spotId) {
    const spot = spotById.get(spotId)
    if (spot) {
      return {
        content: buildSpotDemoReply(spot),
        spotId: spot.id,
        kind: 'spot-recommendation' as const,
      }
    }
  }

  if (type === 'route' || type === 'places') {
    const routeReply = buildRouteDemoReply(
      guideDemoData.spots,
      guideDemoData.route.spotIds,
      mergeVideoDemoRecordSources(recordsDemoData.records),
    )
    return {
      content: routeReply.content,
      spotId: routeReply.nextSpotId,
      kind: routeReply.nextSpotId ? 'spot-recommendation' as const : 'text' as const,
    }
  }

  return {
    content: aiChatDemoData.generalReply,
    kind: 'text' as const,
  }
}

function scheduleDemoReply(type: AiQuestionType, question: string, thinkingId: string) {
  if (replyTimer) clearTimeout(replyTimer)

  replyTimer = setTimeout(() => {
    const reply = buildAssistantReply(type, question)
    replaceMessage(thinkingId, {
      id: createMessageId('assistant'),
      role: 'assistant',
      kind: reply.kind,
      content: reply.content,
      createdAtLabel: formatTimeLabel(),
      status: 'success',
      avatar: aiChatDemoData.assistant.avatar,
      spotId: reply.spotId,
      isDemo: true,
    })
    isGenerating.value = false
    replyTimer = undefined
  }, aiChatDemoData.responseDelayMs)
}

function showGenerationUnavailable(question: string) {
  uni.showToast({
    title: AI_GENERATION_UNAVAILABLE_MESSAGE,
    icon: 'none',
  })
  appendMessage({
    id: createMessageId('assistant-unavailable'),
    role: 'assistant',
    kind: 'text',
    content: aiChatDemoData.generationUnavailableReply,
    createdAtLabel: formatTimeLabel(),
    status: 'success',
    avatar: aiChatDemoData.assistant.avatar,
    sourceQuestionId: question,
    isDemo: true,
  })
}

function submitQuestion(question: string, explicitType?: AiQuestionType) {
  const normalizedQuestion = question.trim()
  if (!normalizedQuestion) {
    uni.showToast({
      title: '请输入问题',
      icon: 'none',
    })
    return
  }
  if (normalizedQuestion.length > 300) {
    uni.showToast({
      title: '问题不能超过300字',
      icon: 'none',
    })
    return
  }
  if (isGenerating.value) {
    uni.showToast({
      title: '正在回复前一个问题',
      icon: 'none',
    })
    return
  }

  const spotId = findSpotIdInQuestion(normalizedQuestion, guideDemoData.spots)
  const questionType = explicitType ?? inferQuestionType(normalizedQuestion, spotId)

  appendMessage({
    id: createMessageId('user'),
    role: 'user',
    kind: 'text',
    content: normalizedQuestion,
    createdAtLabel: formatTimeLabel(),
    status: 'success',
    avatar: USER_AVATAR_PATH,
    isDemo: true,
  })
  currentInput.value = ''

  if (isGenerationQuestionType(questionType)) {
    showGenerationUnavailable(normalizedQuestion)
    return
  }

  isGenerating.value = true
  const thinkingId = createMessageId('assistant-thinking')
  appendMessage({
    id: thinkingId,
    role: 'assistant',
    kind: 'thinking',
    content: '',
    createdAtLabel: formatTimeLabel(),
    status: 'generating',
    avatar: aiChatDemoData.assistant.avatar,
    isDemo: true,
  })
  scheduleDemoReply(questionType, normalizedQuestion, thinkingId)
}

function handleQuickQuestion(question: QuickQuestion) {
  submitQuestion(question.question, question.type)
}

function handleSend() {
  submitQuestion(currentInput.value)
}

function handleViewSpot(spotId: string) {
  uni.navigateTo({
    url: `/pages/spot-detail/index?spotId=${encodeURIComponent(spotId)}`,
  })
}

function handleBack() {
  if (getCurrentPages().length > 1) {
    uni.navigateBack()
    return
  }
  uni.reLaunch({
    url: '/pages/index/index',
  })
}

function handleNavigationSelect(id: HomeNavigationId) {
  if (id === 'ai') return
  if (id === 'home') {
    uni.reLaunch({
      url: '/pages/index/index',
    })
    return
  }
  if (id === 'profile') {
    uni.navigateTo({
      url: '/pages/profile/index',
    })
  }
}

function handleKeyboardHeightChange(height: number) {
  keyboardHeight.value = height
}

onBeforeUnmount(() => {
  if (replyTimer) clearTimeout(replyTimer)
})
</script>

<template>
  <view class="ai-chat-page">
    <AiChatHeader :assistant="aiChatDemoData.assistant" @back="handleBack" />

    <scroll-view
      class="ai-chat-page__messages"
      scroll-y
      enable-back-to-top
      :show-scrollbar="false"
      :scroll-into-view="scrollIntoView"
      :scroll-with-animation="true"
    >
      <view class="ai-chat-page__message-content">
        <view
          v-for="row in messageRows"
          :id="`message-${row.message.id}`"
          :key="row.message.id"
          class="ai-chat-page__message-group"
        >
          <ChatMessageBubble :message="row.message" />
          <SpotRecommendationMessage
            v-if="row.message.kind === 'spot-recommendation' && row.spot"
            :spot="row.spot"
            @view-spot="handleViewSpot"
          />
        </view>

        <QuickQuestionList
          :questions="aiChatDemoData.quickQuestions"
          :disabled="isGenerating"
          @select="handleQuickQuestion"
        />
      </view>
    </scroll-view>

    <view
      class="ai-chat-page__composer-shell"
      :class="{ 'ai-chat-page__composer-shell--keyboard': isKeyboardOpen }"
    >
      <ChatComposer
        v-model="currentInput"
        :disabled="isGenerating"
        placeholder="问问校园点位或游览路线……"
        @send="handleSend"
        @keyboard-height-change="handleKeyboardHeightChange"
      />
    </view>

    <HomeTabBar
      v-if="!isKeyboardOpen"
      :items="homeDemoData.navigation"
      active-id="ai"
      @select="handleNavigationSelect"
    />
  </view>
</template>

<style scoped>
.ai-chat-page {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  flex-direction: column;
  background: #fbf7f1;
  color: #252825;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.ai-chat-page__messages {
  min-height: 0;
  flex: 1;
}

.ai-chat-page__message-content {
  box-sizing: border-box;
  width: 100%;
  min-height: 100%;
  padding: 30rpx 36rpx 44rpx;
}

.ai-chat-page__message-group + .ai-chat-page__message-group {
  margin-top: 28rpx;
}

.ai-chat-page__composer-shell {
  position: relative;
  z-index: 22;
  box-sizing: border-box;
  flex: none;
  margin-bottom: calc(189rpx + env(safe-area-inset-bottom));
  padding: 18rpx 24rpx 20rpx;
  border-top: 2rpx solid #eee8df;
  background: #fbf7f1;
}

.ai-chat-page__composer-shell--keyboard {
  margin-bottom: 0;
  padding-bottom: 14rpx;
}
</style>
