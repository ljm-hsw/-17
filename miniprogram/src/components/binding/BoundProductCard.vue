<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { bindingDemoData } from '../../mocks/binding'
import { guideDemoData } from '../../mocks/guide'
import { buildCheckinOverview, recordsDemoData } from '../../mocks/records'
import type { BoundProduct } from '../../types/binding'

const props = defineProps<{
  product?: BoundProduct
  productImage?: string
  productImageAlt?: string
  todayCheckinCount?: number
  showSuccess?: boolean
}>()

const emit = defineEmits<{
  unbind: []
}>()

const imageLoadFailed = ref(false)
const fallbackTodayCheckinCount = buildCheckinOverview(
  recordsDemoData.records,
  guideDemoData.spots,
).checkedCount

const displayProduct = computed<Readonly<BoundProduct>>(
  () => props.product ?? bindingDemoData.product,
)
const displayProductImage = computed(
  () => props.productImage?.trim() || bindingDemoData.productImage,
)
const displayProductImageAlt = computed(
  () => props.productImageAlt?.trim() || bindingDemoData.productImageAlt,
)
const displayTodayCheckinCount = computed(
  () => props.todayCheckinCount ?? fallbackTodayCheckinCount,
)

watch(displayProductImage, () => {
  imageLoadFailed.value = false
})
</script>

<template>
  <view class="bound-product">
    <view class="bound-product__card">
      <view class="bound-product__status">
        <text class="bound-product__check">✓</text>
        <text>{{ props.showSuccess ? '演示绑定成功' : '已绑定' }}</text>
      </view>

      <view class="bound-product__media">
        <image
          class="bound-product__image"
          :src="displayProductImage"
          :alt="displayProductImageAlt"
          mode="aspectFit"
          @load="imageLoadFailed = false"
          @error="imageLoadFailed = true"
        />
        <view v-if="imageLoadFailed" class="bound-product__image-placeholder">
          <text>文创产品图片暂不可用</text>
        </view>
      </view>

      <text class="bound-product__name">{{ displayProduct.productName }}</text>
      <text class="bound-product__type">{{ displayProduct.productType }}</text>

      <view class="bound-product__details">
        <view class="bound-product__row">
          <text>产品编号</text>
          <text>{{ displayProduct.productCode }}</text>
        </view>
        <view class="bound-product__row">
          <text>绑定时间（演示）</text>
          <text>{{ displayProduct.boundAtLabel }}</text>
        </view>
        <view v-if="displayProduct.lastUsedLabel" class="bound-product__row">
          <text>最近使用</text>
          <text>{{ displayProduct.lastUsedLabel }}</text>
        </view>
        <view class="bound-product__row">
          <text>最近同步（演示）</text>
          <text>{{ displayProduct.lastSyncLabel }}</text>
        </view>
        <view class="bound-product__row">
          <text>今日打卡</text>
          <text class="bound-product__highlight">{{ displayTodayCheckinCount }}次</text>
        </view>
        <view class="bound-product__row">
          <text>产品状态</text>
          <text class="bound-product__highlight">
            {{ displayProduct.isPrimary ? '主产品 · 已绑定' : '已绑定' }}
          </text>
        </view>
      </view>

      <text class="bound-product__disclosure">以上产品、时间和同步信息均为本地演示数据</text>
    </view>

    <button
      class="bound-product__unbind"
      hover-class="bound-product__unbind--pressed"
      @tap="emit('unbind')"
    >
      解除绑定
    </button>
  </view>
</template>

<style scoped>
.bound-product {
  width: 100%;
}

.bound-product__card {
  box-sizing: border-box;
  width: 100%;
  padding: 48rpx 46rpx 42rpx;
  border-radius: 31rpx;
  background: #ffffff;
}

.bound-product__status {
  display: flex;
  align-items: center;
  color: #2e8c73;
  font-size: 42rpx;
  font-weight: 500;
  line-height: 55rpx;
}

.bound-product__check {
  margin-right: 22rpx;
  font-size: 38rpx;
}

.bound-product__media {
  position: relative;
  display: flex;
  width: 390rpx;
  height: 390rpx;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  overflow: hidden;
  background: #fffdf9;
}

.bound-product__image,
.bound-product__image-placeholder {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
}

.bound-product__image-placeholder {
  position: absolute;
  inset: 0;
  border-radius: 24rpx;
  background: #f5f0e9;
  color: #7e776f;
  font-size: 27rpx;
}

.bound-product__name,
.bound-product__type {
  display: block;
  text-align: center;
}

.bound-product__name {
  margin-top: 3rpx;
  color: #333333;
  font-size: 29rpx;
  font-weight: 600;
  line-height: 45rpx;
}

.bound-product__type {
  margin-top: 7rpx;
  color: #858079;
  font-size: 24rpx;
  line-height: 38rpx;
}

.bound-product__details {
  margin-top: 30rpx;
}

.bound-product__row {
  display: flex;
  min-height: 70rpx;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
  color: #333333;
  font-size: 27rpx;
  line-height: 39rpx;
}

.bound-product__row > text:first-child {
  flex: none;
  color: #67625d;
}

.bound-product__row > text:last-child,
.bound-product__row > view:last-child {
  min-width: 0;
  text-align: right;
  word-break: break-all;
}

.bound-product__highlight {
  color: #2e8c73;
  font-weight: 600;
}

.bound-product__disclosure {
  display: block;
  margin-top: 24rpx;
  color: #9a948d;
  font-size: 21rpx;
  line-height: 34rpx;
  text-align: center;
}

.bound-product__unbind {
  display: flex;
  width: calc(100% - 92rpx);
  height: 100rpx;
  align-items: center;
  justify-content: center;
  margin: 76rpx auto 0;
  padding: 0;
  border-radius: 50rpx;
  background: #fffaf2;
  color: #cc8c4d;
  font-size: 31rpx;
  font-weight: 500;
  line-height: 100rpx;
}

.bound-product__unbind::after {
  border: 0;
}

.bound-product__unbind--pressed {
  opacity: 0.7;
}
</style>
