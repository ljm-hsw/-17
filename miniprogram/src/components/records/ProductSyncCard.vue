<script setup lang="ts">
import type { ProductSyncSummary } from '../../types/records'

defineProps<{
  product: ProductSyncSummary
}>()
</script>

<template>
  <view class="product-sync-card">
    <view v-if="product.bindingStatus === 'bound'" class="product-sync-card__content">
      <view class="product-sync-card__product">
        <text class="product-sync-card__label">演示产品</text>
        <text class="product-sync-card__code">{{ product.productCode }}</text>
        <text class="product-sync-card__badge">已绑定</text>
      </view>
      <view class="product-sync-card__sync">
        <text>最近同步（演示）</text>
        <text>{{ product.lastSyncLabel }}</text>
      </view>
    </view>
    <view v-else class="product-sync-card__unbound">
      <text class="product-sync-card__unbound-title">尚未绑定文创产品</text>
      <text class="product-sync-card__unbound-copy">绑定后可查看演示同步信息</text>
    </view>
  </view>
</template>

<style scoped>
.product-sync-card {
  box-sizing: border-box;
  min-height: 125rpx;
  padding: 24rpx 26rpx;
  border-radius: 22rpx;
  background: #fffdfc;
  box-shadow: 0 6rpx 10rpx rgba(164, 143, 126, 0.05);
}

.product-sync-card__content,
.product-sync-card__product,
.product-sync-card__sync {
  display: flex;
  align-items: center;
}

.product-sync-card__content {
  min-height: 77rpx;
  justify-content: space-between;
  gap: 20rpx;
}

.product-sync-card__product {
  min-width: 0;
  flex-wrap: wrap;
  gap: 6rpx 10rpx;
}

.product-sync-card__label,
.product-sync-card__sync {
  color: #7c7670;
  font-size: 26rpx;
}

.product-sync-card__code {
  color: #4e4a46;
  font-size: 28rpx;
  font-weight: 600;
}

.product-sync-card__badge {
  padding: 3rpx 12rpx;
  border-radius: 16rpx;
  background: #eaf6f1;
  color: #2f8f77;
  font-size: 21rpx;
}

.product-sync-card__sync {
  flex: none;
  align-items: flex-end;
  flex-direction: column;
  line-height: 37rpx;
}

.product-sync-card__unbound {
  display: flex;
  min-height: 77rpx;
  justify-content: center;
  flex-direction: column;
}

.product-sync-card__unbound-title {
  color: #4e4a46;
  font-size: 29rpx;
  font-weight: 600;
}

.product-sync-card__unbound-copy {
  margin-top: 6rpx;
  color: #8b857f;
  font-size: 24rpx;
}
</style>
