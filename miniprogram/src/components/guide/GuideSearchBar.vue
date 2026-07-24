<script setup lang="ts">
defineProps<{
  modelValue: string
  placeholder: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function handleInput(event: unknown) {
  const inputEvent = event as { detail: { value: string } }
  emit('update:modelValue', inputEvent.detail.value)
}
</script>

<template>
  <view class="guide-search">
    <image
      class="guide-search__icon"
      src="/static/guide/icon-search.svg"
      alt="搜索"
      mode="aspectFit"
    />
    <input
      class="guide-search__input"
      :value="modelValue"
      :placeholder="placeholder"
      placeholder-class="guide-search__placeholder"
      confirm-type="search"
      @input="handleInput"
    />
  </view>
</template>

<style scoped>
.guide-search {
  box-sizing: border-box;
  display: flex;
  height: 92rpx;
  align-items: center;
  margin: 8rpx 28rpx 0;
  padding: 0 28rpx;
  border-radius: 28rpx;
  background: #ffffff;
  box-shadow: 0 5rpx 12rpx rgba(115, 102, 89, 0.05);
}

.guide-search__icon {
  flex: none;
  width: 38rpx;
  height: 38rpx;
}

.guide-search__input {
  flex: 1;
  height: 92rpx;
  margin-left: 17rpx;
  color: #171816;
  font-size: 27rpx;
  line-height: 92rpx;
}

.guide-search__placeholder {
  color: #a29d96;
  font-size: 27rpx;
}
</style>
