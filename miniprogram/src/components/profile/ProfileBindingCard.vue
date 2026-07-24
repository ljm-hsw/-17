<script setup lang="ts">
import type { BindingStatus } from '../../types/binding'

defineProps<{
  status: BindingStatus
  productCode?: string
}>()

defineEmits<{
  open: []
}>()
</script>

<template>
  <view
    class="profile-binding-card"
    hover-class="profile-binding-card--pressed"
    @tap="$emit('open')"
  >
    <view class="profile-binding-card__icon">
      <text>文</text>
    </view>
    <view class="profile-binding-card__copy">
      <text class="profile-binding-card__title">
        {{ status === 'bound' ? '已绑定文创产品' : '尚未绑定文创产品' }}
      </text>
      <text v-if="status === 'bound' && productCode" class="profile-binding-card__code">
        产品编号：{{ productCode }}
      </text>
    </view>
    <view class="profile-binding-card__right">
      <text class="profile-binding-card__status">
        {{ status === 'bound' ? '已绑定' : '未绑定' }}
      </text>
      <text class="profile-binding-card__action">查看绑定信息 ›</text>
    </view>
  </view>
</template>

<style scoped>
.profile-binding-card {
  display: flex;
  min-height: 184rpx;
  align-items: center;
  box-sizing: border-box;
  padding: 30rpx 30rpx;
  border-radius: 28rpx;
  background: #fffdfc;
  box-shadow: 0 4rpx 20rpx rgba(185, 175, 166, 0.08);
}

.profile-binding-card--pressed {
  opacity: 0.72;
}

.profile-binding-card__icon {
  display: flex;
  width: 84rpx;
  height: 84rpx;
  flex: none;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e8f4ef;
  color: #3c9b80;
  font-size: 30rpx;
  font-weight: 700;
}

.profile-binding-card__copy {
  display: flex;
  min-width: 0;
  flex: 1;
  margin-left: 22rpx;
  flex-direction: column;
}

.profile-binding-card__title {
  color: #625d57;
  font-size: 27rpx;
  font-weight: 600;
  line-height: 40rpx;
}

.profile-binding-card__code {
  margin-top: 5rpx;
  color: #2d2b28;
  font-size: 29rpx;
  font-weight: 700;
  line-height: 44rpx;
  white-space: nowrap;
}

.profile-binding-card__right {
  display: flex;
  flex: none;
  align-items: flex-end;
  margin-left: 14rpx;
  flex-direction: column;
}

.profile-binding-card__status {
  color: #4b927d;
  font-size: 24rpx;
  font-weight: 700;
  line-height: 36rpx;
}

.profile-binding-card__action {
  margin-top: 7rpx;
  color: #8d857e;
  font-size: 21rpx;
  line-height: 32rpx;
  white-space: nowrap;
}
</style>
