<script setup lang="ts">
const emit = defineEmits<{ back: [] }>()
const statusBarHeight = uni.getSystemInfoSync().statusBarHeight ?? 20
</script>

<template>
  <view class="result-header" :style="{ paddingTop: `${statusBarHeight}px` }">
    <view class="result-header__back" @tap="emit('back')">‹</view>
    <text>我的游记</text>
  </view>
</template>

<style scoped>
.result-header { position: relative; z-index: 4; display: flex; height: 92rpx; flex: none; align-items: center; justify-content: center; background: #fbf7f1; color: #23332d; font-size: 34rpx; font-weight: 700; }
.result-header__back { position: absolute; bottom: 8rpx; left: 22rpx; display: flex; width: 72rpx; height: 72rpx; align-items: center; justify-content: center; color: #315f51; font-size: 58rpx; font-weight: 400; }
</style>
