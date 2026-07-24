<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { GuideSpot, SpotCategoryId } from '../../types/guide'
import type { CheckinRecord, CheckinTab } from '../../types/records'

const props = defineProps<{
  spot: GuideSpot
  mode: CheckinTab
  record?: CheckinRecord
}>()

defineEmits<{
  viewDetails: [spotId: string]
  goGuide: [spotId: string]
}>()

const categoryLabels: Record<SpotCategoryId, string> = {
  architecture: '建筑景观',
  sports: '运动场馆',
  study: '学习空间',
  green: '校园绿地',
}

const imageLoadFailed = ref(false)
const categoryLabel = computed(() => categoryLabels[props.spot.category])

watch(
  () => props.spot.id,
  () => {
    imageLoadFailed.value = false
  },
)
</script>

<template>
  <view class="checkin-record-card" @tap="$emit('viewDetails', spot.id)">
    <view class="checkin-record-card__media">
      <image
        v-if="!imageLoadFailed"
        class="checkin-record-card__image"
        :src="spot.coverImage"
        :alt="spot.name"
        mode="aspectFill"
        @error="imageLoadFailed = true"
      />
      <view v-else class="checkin-record-card__placeholder">
        <text>{{ spot.name }}</text>
        <text>图片暂不可用</text>
      </view>
    </view>

    <view class="checkin-record-card__content">
      <view class="checkin-record-card__heading">
        <text class="checkin-record-card__title">{{ spot.name }}</text>
        <view
          v-if="mode === 'checked' && record"
          class="checkin-record-card__method"
          :class="`checkin-record-card__method--${record.method}`"
        >
          <text>{{ record.methodLabel }}</text>
          <text class="checkin-record-card__demo">· 演示</text>
        </view>
        <text v-else class="checkin-record-card__pending">尚未打卡</text>
      </view>

      <view class="checkin-record-card__classification">
        <text>{{ categoryLabel }}</text>
        <text v-if="spot.tags[0]">· {{ spot.tags[0] }}</text>
      </view>

      <template v-if="mode === 'checked' && record">
        <text class="checkin-record-card__time">{{ record.checkedAtLabel }}</text>
        <view class="checkin-record-card__footer">
          <text class="checkin-record-card__uid">
            卡片UID：{{ record.maskedCardUid ?? '未提供' }}
          </text>
          <view
            class="checkin-record-card__detail"
            @tap.stop="$emit('viewDetails', spot.id)"
          >
            <text>查看详情</text>
          </view>
        </view>
      </template>

      <view v-else class="checkin-record-card__unchecked-actions">
        <view class="checkin-record-card__text-action" @tap.stop="$emit('viewDetails', spot.id)">
          <text>查看详情</text>
        </view>
        <view class="checkin-record-card__guide-action" @tap.stop="$emit('goGuide', spot.id)">
          <text>前往导览</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.checkin-record-card {
  display: flex;
  box-sizing: border-box;
  min-height: 272rpx;
  padding: 9rpx;
  border-radius: 22rpx;
  background: #fffdfc;
  box-shadow: 0 6rpx 10rpx rgba(164, 143, 126, 0.06);
}

.checkin-record-card__media {
  width: 207rpx;
  min-height: 240rpx;
  flex: none;
  overflow: hidden;
  border-radius: 18rpx;
  background: #eee8e1;
}

.checkin-record-card__image,
.checkin-record-card__placeholder {
  width: 100%;
  height: 100%;
}

.checkin-record-card__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #8a847d;
  font-size: 22rpx;
  line-height: 35rpx;
  text-align: center;
}

.checkin-record-card__content {
  display: flex;
  min-width: 0;
  flex: 1;
  justify-content: center;
  flex-direction: column;
  padding: 16rpx 16rpx 14rpx 30rpx;
}

.checkin-record-card__heading,
.checkin-record-card__classification,
.checkin-record-card__footer,
.checkin-record-card__unchecked-actions {
  display: flex;
  align-items: center;
}

.checkin-record-card__heading {
  align-items: flex-start;
  justify-content: space-between;
  gap: 12rpx;
}

.checkin-record-card__title {
  min-width: 0;
  color: #22211f;
  font-size: 35rpx;
  font-weight: 700;
  line-height: 48rpx;
}

.checkin-record-card__method,
.checkin-record-card__pending {
  flex: none;
  padding: 7rpx 13rpx;
  border-radius: 24rpx;
  background: #eaf6f1;
  color: #2f8f77;
  font-size: 21rpx;
  line-height: 30rpx;
}

.checkin-record-card__method--camera-assisted {
  background: #edf3fb;
  color: #55789a;
}

.checkin-record-card__method--device-recognition {
  background: #f4efe8;
  color: #856d51;
}

.checkin-record-card__demo {
  opacity: 0.78;
}

.checkin-record-card__pending {
  background: #f3eee8;
  color: #817a73;
}

.checkin-record-card__classification {
  gap: 10rpx;
  margin-top: 5rpx;
  color: #948c84;
  font-size: 22rpx;
  line-height: 33rpx;
}

.checkin-record-card__time {
  margin-top: 8rpx;
  color: #7c7670;
  font-size: 30rpx;
  line-height: 42rpx;
}

.checkin-record-card__footer {
  justify-content: space-between;
  gap: 10rpx;
  margin-top: 15rpx;
}

.checkin-record-card__uid {
  min-width: 0;
  color: #7c7670;
  font-size: 24rpx;
  line-height: 38rpx;
}

.checkin-record-card__detail,
.checkin-record-card__text-action,
.checkin-record-card__guide-action {
  display: flex;
  height: 56rpx;
  align-items: center;
  justify-content: center;
  padding: 0 15rpx;
  border-radius: 15rpx;
  font-size: 22rpx;
  white-space: nowrap;
}

.checkin-record-card__detail {
  flex: none;
  background: #eaf6f1;
  color: #2f8f77;
}

.checkin-record-card__unchecked-actions {
  justify-content: flex-end;
  gap: 12rpx;
  margin-top: 26rpx;
}

.checkin-record-card__text-action {
  border: 2rpx solid #e2d9cf;
  color: #746d66;
}

.checkin-record-card__guide-action {
  background: #43ae91;
  color: #ffffff;
  font-weight: 600;
}
</style>
