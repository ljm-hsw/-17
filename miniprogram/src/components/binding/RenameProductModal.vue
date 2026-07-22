<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  currentAlias: string
}>()

const emit = defineEmits<{
  cancel: []
  save: [alias: string]
}>()

const alias = ref(props.currentAlias)
const error = ref('')

const systemInfo = uni.getSystemInfoSync()
const windowHeight = systemInfo.windowHeight || systemInfo.screenHeight
const statusBarHeight = systemInfo.statusBarHeight ?? 20
let protectedTop = statusBarHeight + 56

try {
  const menuButton = uni.getMenuButtonBoundingClientRect()
  if (menuButton.bottom > 0) {
    protectedTop = menuButton.bottom + 12
  }
} catch {
  protectedTop = statusBarHeight + 56
}

const safeBottom = Math.max(0, windowHeight - (systemInfo.safeArea?.bottom ?? windowHeight))
const layerStyle = {
  paddingTop: `${protectedTop}px`,
  paddingBottom: `${safeBottom + 12}px`,
}

function handleInput(event: Event) {
  const detail = (event as Event & { detail?: { value?: unknown } }).detail
  alias.value = typeof detail?.value === 'string' ? detail.value : ''
  if (error.value) error.value = ''
}

function handleSave() {
  const normalizedAlias = alias.value.trim()
  if (!normalizedAlias) {
    error.value = '请输入产品别名'
    return
  }
  if (normalizedAlias.length > 20) {
    error.value = '产品别名不能超过20个字符'
    return
  }
  emit('save', normalizedAlias)
}
</script>

<template>
  <view class="rename-layer" :style="layerStyle" @tap="emit('cancel')">
    <view class="rename-modal" @tap.stop>
      <view class="rename-modal__heading">
        <text class="rename-modal__title">修改产品别名</text>
        <view
          class="rename-modal__close"
          hover-class="rename-modal__close--pressed"
          aria-label="关闭"
          @tap="emit('cancel')"
        >
          <text>×</text>
        </view>
      </view>

      <text class="rename-modal__description">别名仅在当前页面本地演示，不会保存到服务器。</text>
      <input
        class="rename-modal__input"
        :class="{ 'rename-modal__input--error': error }"
        :value="alias"
        maxlength="20"
        focus
        placeholder="请输入1—20个字符"
        placeholder-class="rename-modal__placeholder"
        @input="handleInput"
      />
      <text v-if="error" class="rename-modal__error">{{ error }}</text>

      <view class="rename-modal__actions">
        <button
          class="rename-modal__button rename-modal__button--secondary"
          hover-class="rename-modal__button--pressed"
          @tap="emit('cancel')"
        >
          取消
        </button>
        <button
          class="rename-modal__button rename-modal__button--primary"
          hover-class="rename-modal__button--pressed"
          @tap="handleSave"
        >
          保存
        </button>
      </view>
    </view>
  </view>
</template>

<style scoped>
.rename-layer {
  position: fixed;
  z-index: 80;
  display: flex;
  box-sizing: border-box;
  align-items: center;
  justify-content: center;
  padding-right: 44rpx;
  padding-left: 44rpx;
  background: rgba(34, 31, 28, 0.42);
  inset: 0;
}

.rename-modal {
  box-sizing: border-box;
  width: 100%;
  max-height: 100%;
  padding: 38rpx 38rpx 42rpx;
  border-radius: 32rpx;
  background: #fffefc;
}

.rename-modal__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rename-modal__title {
  color: #333333;
  font-size: 35rpx;
  font-weight: 700;
}

.rename-modal__close {
  display: flex;
  width: 60rpx;
  height: 60rpx;
  align-items: center;
  justify-content: center;
  margin-left: 20rpx;
  border-radius: 50%;
  background: #f1ebe3;
  color: #6c665f;
  font-size: 46rpx;
  line-height: 60rpx;
}

.rename-modal__close--pressed {
  opacity: 0.66;
}

.rename-modal__description {
  display: block;
  margin-top: 20rpx;
  color: #817b74;
  font-size: 24rpx;
  line-height: 39rpx;
}

.rename-modal__input {
  box-sizing: border-box;
  width: 100%;
  height: 88rpx;
  margin-top: 28rpx;
  padding: 0 24rpx;
  border: 2rpx solid #ded8d0;
  border-radius: 18rpx;
  background: #ffffff;
  color: #333333;
  font-size: 27rpx;
}

.rename-modal__input--error {
  border-color: #c86f5d;
}

.rename-modal__placeholder {
  color: #aaa39b;
}

.rename-modal__error {
  display: block;
  margin-top: 9rpx;
  color: #b95d4b;
  font-size: 23rpx;
}

.rename-modal__actions {
  display: flex;
  gap: 24rpx;
  margin-top: 34rpx;
}

.rename-modal__button {
  display: flex;
  height: 84rpx;
  flex: 1;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 0;
  border-radius: 44rpx;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 84rpx;
}

.rename-modal__button::after {
  border: 0;
}

.rename-modal__button--secondary {
  border: 2rpx solid #ddd6ce;
  background: #fffefc;
  color: #625d57;
}

.rename-modal__button--primary {
  background: #2e8c73;
  color: #ffffff;
}

.rename-modal__button--pressed {
  opacity: 0.74;
}
</style>
