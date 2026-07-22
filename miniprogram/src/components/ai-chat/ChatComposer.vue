<script setup lang="ts">
withDefaults(defineProps<{
  modelValue: string
  disabled: boolean
  placeholder?: string
}>(), {
  placeholder: '问问校园点位或游览路线……',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  send: []
  focus: []
  keyboardHeightChange: [height: number]
}>()

interface TextareaInputEventDetail {
  detail: {
    value: string
  }
}

interface KeyboardHeightEventDetail {
  detail: {
    height: number
  }
}

function handleInput(event: Event) {
  const inputEvent = event as Event & TextareaInputEventDetail
  emit('update:modelValue', inputEvent.detail.value)
}

function handleKeyboardHeightChange(event: Event) {
  const keyboardEvent = event as Event & KeyboardHeightEventDetail
  emit('keyboardHeightChange', Math.max(0, keyboardEvent.detail.height || 0))
}
</script>

<template>
  <view class="chat-composer">
    <textarea
      class="chat-composer__textarea"
      :value="modelValue"
      :disabled="disabled"
      :placeholder="placeholder"
      placeholder-class="chat-composer__placeholder"
      :maxlength="300"
      :auto-height="true"
      :adjust-position="true"
      :cursor-spacing="24"
      confirm-type="send"
      fixed
      @input="handleInput"
      @focus="$emit('focus')"
      @confirm="$emit('send')"
      @keyboardheightchange="handleKeyboardHeightChange"
    />
    <view
      class="chat-composer__send"
      :class="{ 'chat-composer__send--disabled': disabled }"
      hover-class="chat-composer__pressed"
      aria-label="发送"
      @tap="!disabled && $emit('send')"
    >
      <text>↑</text>
    </view>
  </view>
</template>

<style scoped>
.chat-composer {
  display: flex;
  align-items: flex-end;
  gap: 12rpx;
}

.chat-composer__textarea {
  box-sizing: border-box;
  min-height: 86rpx;
  max-height: 152rpx;
  flex: 1;
  padding: 21rpx 28rpx;
  border: 2rpx solid #ece7e0;
  border-radius: 44rpx;
  background: #ffffff;
  box-shadow: 0 4rpx 16rpx rgba(108, 98, 87, 0.06);
  color: #454945;
  font-size: 25rpx;
  line-height: 40rpx;
}

.chat-composer__placeholder {
  color: #aaa69f;
}

.chat-composer__send {
  display: flex;
  width: 76rpx;
  height: 76rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.chat-composer__send {
  background: #50aa91;
  box-shadow: 0 5rpx 12rpx rgba(80, 170, 145, 0.2);
  color: #ffffff;
  font-size: 38rpx;
  font-weight: 800;
}

.chat-composer__send--disabled {
  background: #a9c8bd;
  box-shadow: none;
}

.chat-composer__pressed {
  opacity: 0.68;
}
</style>
