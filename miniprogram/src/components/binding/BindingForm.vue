<script setup lang="ts">
import { computed } from 'vue'
import type {
  BindingFormErrors,
  BindingFormValue,
  BindingOperationStatus,
} from '../../types/binding'

const props = defineProps<{
  value: BindingFormValue
  errors: BindingFormErrors
  operationStatus: BindingOperationStatus
}>()

const emit = defineEmits<{
  uidChange: [value: string]
  submit: []
}>()

const submitLabel = computed(() => {
  if (props.operationStatus === 'binding') return '演示绑定中'
  if (props.operationStatus === 'error') return '重新演示绑定'
  return '立即绑定'
})

function readInputValue(event: Event) {
  const detail = (event as Event & { detail?: { value?: unknown } }).detail
  return typeof detail?.value === 'string' ? detail.value : ''
}

function handleUidInput(event: Event) {
  emit('uidChange', readInputValue(event))
}

</script>

<template>
  <view class="binding-form">
    <view class="binding-form__field">
      <text class="binding-form__label">卡片UID</text>
      <input
        class="binding-form__input"
        :class="{ 'binding-form__input--error': errors.uid }"
        :value="value.uid"
        maxlength="24"
        placeholder="请输入卡片UID"
        placeholder-class="binding-form__placeholder"
        :disabled="operationStatus === 'binding'"
        @input="handleUidInput"
      />
      <text v-if="errors.uid" class="binding-form__error">{{ errors.uid }}</text>
    </view>

    <text v-if="operationStatus === 'error'" class="binding-form__operation-error">
      演示绑定失败，请检查后重试
    </text>

    <button
      class="binding-form__submit"
      hover-class="binding-form__submit--pressed"
      :disabled="operationStatus === 'binding'"
      :loading="operationStatus === 'binding'"
      @tap="emit('submit')"
    >
      {{ submitLabel }}
    </button>
  </view>
</template>

<style scoped>
.binding-form {
  margin-top: 30rpx;
}

.binding-form__label {
  display: block;
  color: #3f3d3a;
  font-size: 27rpx;
  font-weight: 600;
  line-height: 42rpx;
}

.binding-form__input {
  box-sizing: border-box;
  width: 100%;
  height: 88rpx;
  margin-top: 12rpx;
  padding: 0 26rpx;
  border: 2rpx solid #e5dfd8;
  border-radius: 18rpx;
  background: #fffdfb;
  color: #333333;
  font-size: 27rpx;
}

.binding-form__input--error {
  border-color: #c86f5d;
}

.binding-form__placeholder {
  color: #aaa39b;
  font-size: 25rpx;
}

.binding-form__error,
.binding-form__operation-error {
  display: block;
  margin-top: 9rpx;
  color: #b95d4b;
  font-size: 23rpx;
  line-height: 35rpx;
}

.binding-form__operation-error {
  text-align: center;
}

.binding-form__submit {
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
  font-weight: 600;
  line-height: 100rpx;
}

.binding-form__submit::after {
  border: 0;
}

.binding-form__submit[disabled] {
  background: #91bbae;
  color: rgba(255, 255, 255, 0.9);
}

.binding-form__submit--pressed {
  opacity: 0.78;
}
</style>
