<script setup lang="ts">
import { ref } from 'vue'
import BindingForm from './BindingForm.vue'
import BindingMethodTabs from './BindingMethodTabs.vue'
import type {
  BindingFormErrors,
  BindingFormValue,
  BindingMethod,
  BindingOperationStatus,
} from '../../types/binding'

defineProps<{
  productImage: string
  productImageAlt: string
  purposes: readonly string[]
  bindingNotes: readonly string[]
  method: BindingMethod
  formValue: BindingFormValue
  formErrors: BindingFormErrors
  operationStatus: BindingOperationStatus
}>()

const emit = defineEmits<{
  selectMethod: [method: BindingMethod]
  uidChange: [value: string]
  submit: []
  readNfc: []
}>()

const imageLoadFailed = ref(false)
</script>

<template>
  <view class="unbound-card">
    <view class="unbound-card__media">
      <image
        v-if="!imageLoadFailed"
        class="unbound-card__image"
        :src="productImage"
        :alt="productImageAlt"
        mode="aspectFit"
        @error="imageLoadFailed = true"
      />
      <view v-else class="unbound-card__image-placeholder">
        <text>文创产品</text>
      </view>
    </view>

    <text class="unbound-card__title">绑定文创产品</text>
    <text class="unbound-card__subtitle">完成演示绑定后，可查看当前产品信息</text>

    <view class="unbound-card__purposes">
      <view v-for="purpose in purposes" :key="purpose" class="unbound-card__purpose">
        <view class="unbound-card__purpose-dot" />
        <text>{{ purpose }}</text>
      </view>
    </view>

    <view class="unbound-card__method">
      <text class="unbound-card__section-title">选择绑定方式</text>
      <BindingMethodTabs :active-method="method" @select="emit('selectMethod', $event)" />
    </view>

    <BindingForm
      v-if="method === 'manual'"
      :value="formValue"
      :errors="formErrors"
      :operation-status="operationStatus"
      @uid-change="emit('uidChange', $event)"
      @submit="emit('submit')"
    />

    <view v-else class="unbound-card__nfc">
      <text class="unbound-card__nfc-title">将文创产品靠近手机感应区域</text>
      <text class="unbound-card__nfc-copy">当前仅提供演示入口，不会调用真实NFC能力。</text>
      <button
        class="unbound-card__nfc-button"
        hover-class="unbound-card__nfc-button--pressed"
        @tap="emit('readNfc')"
      >
        开始读取
      </button>
    </view>

    <view class="unbound-card__notes">
      <text class="unbound-card__section-title">绑定说明</text>
      <text v-for="note in bindingNotes" :key="note" class="unbound-card__note">{{ note }}</text>
    </view>
  </view>
</template>

<style scoped>
.unbound-card {
  box-sizing: border-box;
  width: 100%;
  padding: 40rpx 46rpx 46rpx;
  border-radius: 31rpx;
  background: #ffffff;
}

.unbound-card__media {
  display: flex;
  width: 300rpx;
  height: 300rpx;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  overflow: hidden;
  background: #fffdf9;
}

.unbound-card__image,
.unbound-card__image-placeholder {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
}

.unbound-card__image-placeholder {
  border-radius: 24rpx;
  background: #f5f0e9;
  color: #7e776f;
  font-size: 27rpx;
}

.unbound-card__title,
.unbound-card__subtitle {
  display: block;
  text-align: center;
}

.unbound-card__title {
  margin-top: 18rpx;
  color: #333333;
  font-size: 40rpx;
  font-weight: 700;
  line-height: 58rpx;
}

.unbound-card__subtitle {
  margin-top: 8rpx;
  color: #858079;
  font-size: 24rpx;
  line-height: 38rpx;
}

.unbound-card__purposes {
  margin-top: 30rpx;
  padding: 22rpx 24rpx;
  border-radius: 20rpx;
  background: #f4faf7;
}

.unbound-card__purpose {
  display: flex;
  align-items: flex-start;
  color: #5b635f;
  font-size: 24rpx;
  line-height: 40rpx;
}

.unbound-card__purpose + .unbound-card__purpose {
  margin-top: 8rpx;
}

.unbound-card__purpose-dot {
  width: 9rpx;
  height: 9rpx;
  flex: none;
  margin: 15rpx 14rpx 0 0;
  border-radius: 50%;
  background: #2e8c73;
}

.unbound-card__method,
.unbound-card__notes {
  margin-top: 34rpx;
}

.unbound-card__section-title {
  display: block;
  margin-bottom: 16rpx;
  color: #44413d;
  font-size: 27rpx;
  font-weight: 700;
  line-height: 42rpx;
}

.unbound-card__nfc {
  display: flex;
  align-items: center;
  flex-direction: column;
  margin-top: 30rpx;
  padding: 34rpx 24rpx 6rpx;
  text-align: center;
}

.unbound-card__nfc-title {
  color: #3d3a37;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 44rpx;
}

.unbound-card__nfc-copy {
  margin-top: 12rpx;
  color: #8f8982;
  font-size: 24rpx;
  line-height: 39rpx;
}

.unbound-card__nfc-button {
  display: flex;
  width: 100%;
  height: 100rpx;
  align-items: center;
  justify-content: center;
  margin-top: 34rpx;
  padding: 0;
  border-radius: 50rpx;
  background: #2e8c73;
  color: #ffffff;
  font-size: 31rpx;
  line-height: 100rpx;
}

.unbound-card__nfc-button::after {
  border: 0;
}

.unbound-card__nfc-button--pressed {
  opacity: 0.78;
}

.unbound-card__notes {
  padding-top: 28rpx;
  border-top: 2rpx solid #eee8e1;
}

.unbound-card__note {
  display: block;
  color: #89837c;
  font-size: 23rpx;
  line-height: 38rpx;
}

.unbound-card__note + .unbound-card__note {
  margin-top: 6rpx;
}
</style>
