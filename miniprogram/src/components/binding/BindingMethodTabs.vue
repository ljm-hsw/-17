<script setup lang="ts">
import type { BindingMethod } from '../../types/binding'

defineProps<{
  activeMethod: BindingMethod
}>()

const emit = defineEmits<{
  select: [method: BindingMethod]
}>()
</script>

<template>
  <view class="method-tabs" aria-label="绑定方式">
    <view
      class="method-tabs__item"
      :class="{ 'method-tabs__item--active': activeMethod === 'manual' }"
      hover-class="method-tabs__item--pressed"
      @tap="emit('select', 'manual')"
    >
      <text>手动输入</text>
    </view>
    <view
      class="method-tabs__item"
      :class="{ 'method-tabs__item--active': activeMethod === 'nfc' }"
      hover-class="method-tabs__item--pressed"
      @tap="emit('select', 'nfc')"
    >
      <text>NFC读取</text>
    </view>
  </view>
</template>

<style scoped>
.method-tabs {
  display: flex;
  box-sizing: border-box;
  width: 100%;
  padding: 7rpx;
  border-radius: 48rpx;
  background: #f4eee7;
}

.method-tabs__item {
  display: flex;
  height: 76rpx;
  flex: 1;
  align-items: center;
  justify-content: center;
  border-radius: 40rpx;
  color: #77716a;
  font-size: 27rpx;
  font-weight: 500;
}

.method-tabs__item--active {
  background: #ffffff;
  color: #2e8c73;
  font-weight: 700;
}

.method-tabs__item--pressed {
  opacity: 0.72;
}
</style>
