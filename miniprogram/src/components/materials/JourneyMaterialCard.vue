<script setup lang="ts">
import { ref, watch } from 'vue'
import type { JourneyMaterialItem } from '../../types/materials'

const props = defineProps<{ item: JourneyMaterialItem }>()
const emit = defineEmits<{ preview: [image: string] }>()
const imageLoadFailed = ref(false)

watch(() => props.item.id, () => { imageLoadFailed.value = false })

function handlePreview() {
  if (props.item.image && !imageLoadFailed.value) emit('preview', props.item.image)
}
</script>

<template>
  <view class="material-card">
    <view class="material-card__media" @tap="handlePreview">
      <image
        v-if="item.image && !imageLoadFailed"
        class="material-card__image"
        :src="item.image"
        :alt="`${item.spotName}旅程影像`"
        mode="aspectFill"
        @error="imageLoadFailed = true"
      />
      <view v-else class="material-card__placeholder">
        <text class="material-card__placeholder-title">等待实际拍摄照片</text>
        <text>后续放入本地素材后即可预览</text>
      </view>
      <text class="material-card__spot">{{ item.spotName }}</text>
    </view>

    <view class="material-card__details">
      <view class="material-card__row">
        <text>拍摄时间</text><text>{{ item.capturedAtLabel }}</text>
      </view>
      <view class="material-card__row">
        <text>姿势任务</text><text>{{ item.pose.name }}</text>
      </view>
      <view class="material-card__pose">
        <image :src="item.pose.image" :alt="item.pose.name" mode="aspectFit" />
        <text>{{ item.pose.instruction }}</text>
      </view>
      <view class="material-card__linked">
        <text>✓</text><text>{{ item.linkedToCheckin ? '已关联演示打卡点位' : '待关联点位' }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.material-card { overflow: hidden; border-radius: 28rpx; background: #fffdf9; box-shadow: 0 7rpx 24rpx rgba(112, 95, 78, 0.08); }
.material-card__media { position: relative; height: 310rpx; overflow: hidden; background: #eee9e1; }
.material-card__image, .material-card__placeholder { width: 100%; height: 100%; }
.material-card__placeholder { display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 8rpx; color: #999087; font-size: 23rpx; }
.material-card__placeholder-title { color: #68625c; font-size: 28rpx; font-weight: 700; }
.material-card__spot { position: absolute; bottom: 18rpx; left: 20rpx; padding: 7rpx 16rpx; border-radius: 20rpx; background: rgba(38, 91, 75, 0.88); color: #fff; font-size: 24rpx; font-weight: 700; }
.material-card__details { padding: 22rpx 24rpx 25rpx; }
.material-card__row { display: flex; min-height: 48rpx; align-items: center; justify-content: space-between; color: #736c65; font-size: 24rpx; }
.material-card__row text:last-child { color: #3f4945; font-weight: 600; }
.material-card__pose { display: flex; align-items: center; gap: 18rpx; margin-top: 13rpx; padding: 14rpx; border-radius: 20rpx; background: #f2f8f5; color: #63706b; font-size: 23rpx; line-height: 35rpx; }
.material-card__pose image { width: 104rpx; height: 104rpx; flex: none; border-radius: 16rpx; }
.material-card__linked { display: flex; align-items: center; gap: 9rpx; margin-top: 16rpx; color: #378a73; font-size: 22rpx; font-weight: 700; }
</style>
