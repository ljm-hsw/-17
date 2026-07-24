<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import BindingHeader from '../../components/binding/BindingHeader.vue'
import BoundProductCard from '../../components/binding/BoundProductCard.vue'
import UnboundProductCard from '../../components/binding/UnboundProductCard.vue'
import { bindingDemoData } from '../../mocks/binding'
import { guideDemoData } from '../../mocks/guide'
import { buildCheckinOverview, recordsDemoData } from '../../mocks/records'
import type {
  BindingFormErrors,
  BindingFormValue,
  BindingMethod,
  BindingMockScenario,
  BindingPageState,
} from '../../types/binding'

// 开发演示开关：改为 failure 可明确触发失败流程；正式默认流程保持 success。
const MOCK_BINDING_SCENARIO = ref<BindingMockScenario>('success')

const state = reactive<BindingPageState>({
  status: bindingDemoData.initialStatus,
  method: bindingDemoData.defaultMethod,
  operationStatus: 'idle',
  product: { ...bindingDemoData.product },
})

const formValue = reactive<BindingFormValue>({
  uid: '',
})

const formErrors = reactive<BindingFormErrors>({})

const todayCheckinCount = computed(() => {
  return buildCheckinOverview(recordsDemoData.records, guideDemoData.spots).checkedCount
})

function handleBack() {
  uni.navigateBack()
}

function clearFormErrors() {
  formErrors.uid = undefined
}

function setMethod(method: BindingMethod) {
  if (state.operationStatus === 'binding') return
  state.method = method
  state.operationStatus = 'idle'
  clearFormErrors()
}

function updateUid(value: string) {
  formValue.uid = value
  formErrors.uid = undefined
  if (state.operationStatus === 'error') state.operationStatus = 'idle'
}

function validateForm() {
  clearFormErrors()

  const uid = formValue.uid.trim().toUpperCase()

  formValue.uid = uid

  if (!uid) {
    formErrors.uid = '请输入卡片UID'
  } else if (!/^[0-9A-F]{8,20}$/.test(uid)) {
    formErrors.uid = '请输入8—20位十六进制卡片UID'
  }

  return !formErrors.uid
}

function handleManualBinding() {
  if (state.operationStatus === 'binding') return
  if (!validateForm()) return

  state.operationStatus = 'binding'

  setTimeout(() => {
    if (MOCK_BINDING_SCENARIO.value === 'failure') {
      state.operationStatus = 'error'
      uni.showToast({
        title: '演示绑定失败，请重试',
        icon: 'none',
      })
      return
    }

    state.product = {
      ...state.product,
      maskedUid: `••••${formValue.uid.slice(-4)}`,
    }
    state.operationStatus = 'success'
    state.status = 'bound'

    uni.showToast({
      title: '演示绑定成功',
      icon: 'success',
      duration: 1000,
    })

    setTimeout(() => {
      if (state.status === 'bound') state.operationStatus = 'idle'
    }, 1200)
  }, 800)
}

function showNfcPlaceholder() {
  uni.showToast({
    title: 'NFC读取功能待真机接入',
    icon: 'none',
  })
}

function handleUnbind() {
  uni.showModal({
    title: '解除绑定',
    content: '当前为本地演示操作。解除绑定不会删除已有打卡记录，是否继续？',
    confirmText: '继续解除',
    confirmColor: '#CC8C4D',
    success: (result) => {
      if (!result.confirm) return

      state.status = 'unbound'
      state.method = bindingDemoData.defaultMethod
      state.operationStatus = 'idle'
      formValue.uid = ''
      clearFormErrors()

      uni.showToast({
        title: '演示解除成功',
        icon: 'none',
      })
    },
  })
}

</script>

<template>
  <view class="binding-page">
    <BindingHeader @back="handleBack" />

    <scroll-view class="binding-page__scroll" scroll-y enable-back-to-top>
      <view class="binding-page__content">
        <BoundProductCard
          v-if="state.status === 'bound'"
          :product="state.product"
          :product-image="bindingDemoData.productImage"
          :product-image-alt="bindingDemoData.productImageAlt"
          :today-checkin-count="todayCheckinCount"
          :show-success="state.operationStatus === 'success'"
          @unbind="handleUnbind"
        />

        <UnboundProductCard
          v-else
          :product-image="bindingDemoData.productImage"
          :product-image-alt="bindingDemoData.productImageAlt"
          :purposes="bindingDemoData.purposes"
          :binding-notes="bindingDemoData.bindingNotes"
          :method="state.method"
          :form-value="formValue"
          :form-errors="formErrors"
          :operation-status="state.operationStatus"
          @select-method="setMethod"
          @uid-change="updateUid"
          @submit="handleManualBinding"
          @read-nfc="showNfcPlaceholder"
        />
      </view>
    </scroll-view>

  </view>
</template>

<style scoped>
.binding-page {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  flex-direction: column;
  background: #faf5f0;
  color: #333333;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.binding-page__scroll {
  width: 100%;
  min-height: 0;
  flex: 1;
  overflow-x: hidden;
}

.binding-page__content {
  box-sizing: border-box;
  width: 100%;
  padding: 38rpx 54rpx calc(72rpx + env(safe-area-inset-bottom));
}
</style>
