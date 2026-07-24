<script setup lang="ts">
import { ref, watch } from 'vue'
import AiThinkingIndicator from './AiThinkingIndicator.vue'
import type { ChatMessage } from '../../types/ai-chat'

const props = defineProps<{
  message: ChatMessage
}>()

defineEmits<{
  retry: [messageId: string]
}>()

const avatarLoadFailed = ref(false)

watch(
  () => props.message.avatar,
  () => {
    avatarLoadFailed.value = false
  },
)
</script>

<template>
  <view
    class="chat-message"
    :class="{
      'chat-message--user': message.role === 'user',
      'chat-message--assistant': message.role === 'assistant',
    }"
  >
    <view class="chat-message__avatar">
      <image
        v-if="!avatarLoadFailed"
        :src="message.avatar"
        :alt="message.role === 'assistant' ? '倾梦小游头像' : '演示用户头像'"
        mode="aspectFill"
        @error="avatarLoadFailed = true"
      />
      <text v-else>{{ message.role === 'assistant' ? 'AI' : '我' }}</text>
    </view>

    <view class="chat-message__body">
      <view
        class="chat-message__bubble"
        :class="{
          'chat-message__bubble--user': message.role === 'user',
          'chat-message__bubble--error': message.status === 'error',
        }"
      >
        <text
          v-if="message.role === 'assistant'"
          class="chat-message__demo-label"
        >前端演示回复</text>
        <AiThinkingIndicator v-if="message.kind === 'thinking'" />
        <text v-else class="chat-message__content">{{ message.content }}</text>
        <view
          v-if="message.status === 'error' && message.retryable"
          class="chat-message__retry"
          hover-class="chat-message__retry--pressed"
          @tap="$emit('retry', message.id)"
        >
          <text>重新生成</text>
        </view>
      </view>
      <text class="chat-message__time">{{ message.createdAtLabel }}</text>
    </view>
  </view>
</template>

<style scoped>
.chat-message {
  display: flex;
  width: 100%;
  align-items: flex-start;
  gap: 16rpx;
}

.chat-message--user {
  flex-direction: row-reverse;
}

.chat-message__avatar {
  display: flex;
  width: 76rpx;
  height: 76rpx;
  overflow: hidden;
  flex: none;
  align-items: center;
  justify-content: center;
  border: 2rpx solid rgba(89, 135, 120, 0.12);
  border-radius: 50%;
  background: #eaf3ef;
  color: #4b8a78;
  font-size: 22rpx;
  font-weight: 700;
}

.chat-message__avatar image {
  width: 100%;
  height: 100%;
}

.chat-message__body {
  display: flex;
  max-width: 76%;
  min-width: 0;
  align-items: flex-start;
  flex-direction: column;
}

.chat-message--user .chat-message__body {
  align-items: flex-end;
  max-width: 72%;
}

.chat-message__bubble {
  box-sizing: border-box;
  max-width: 100%;
  padding: 23rpx 27rpx;
  border-radius: 30rpx 30rpx 30rpx 10rpx;
  background: #fffdf9;
  box-shadow: 0 4rpx 8rpx rgba(108, 98, 87, 0.08);
}

.chat-message__bubble--user {
  border-radius: 30rpx 30rpx 10rpx 30rpx;
  background: #68a7bf;
  box-shadow: 0 4rpx 7rpx rgba(90, 127, 141, 0.12);
  color: #ffffff;
}

.chat-message__bubble--error {
  border: 2rpx solid #ead8ce;
  background: #fff9f5;
}

.chat-message__demo-label {
  display: block;
  margin-bottom: 9rpx;
  color: #4b927e;
  font-size: 19rpx;
  font-weight: 700;
  line-height: 27rpx;
  white-space: nowrap;
}

.chat-message__content {
  color: #505550;
  font-size: 27rpx;
  line-height: 45rpx;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.chat-message__bubble--user .chat-message__content {
  color: #ffffff;
}

.chat-message__time {
  margin-top: 8rpx;
  color: #b0aca5;
  font-size: 19rpx;
  line-height: 27rpx;
}

.chat-message__retry {
  display: flex;
  width: fit-content;
  height: 54rpx;
  align-items: center;
  justify-content: center;
  margin-top: 14rpx;
  padding: 0 22rpx;
  border-radius: 28rpx;
  background: #eaf5f1;
  color: #35836f;
  font-size: 22rpx;
  font-weight: 700;
}

.chat-message__retry--pressed {
  opacity: 0.68;
}
</style>
