<script setup lang="ts">
import type { Scene, Spot } from '../../types/content'

defineProps<{ scene: Scene; spots: Spot[]; selectedId?: string }>()
defineEmits<{ select: [spot: Spot] }>()
</script>

<template>
  <div class="map-panel">
    <img v-if="scene.map_image_url" :src="scene.map_image_url" :alt="`${scene.name}运营地图`" />
    <div v-else class="map-placeholder"><strong>{{ scene.name }}</strong><span>尚未设置地图图片</span></div>
    <button
      v-for="spot in spots"
      :key="spot.id"
      type="button"
      class="spot-pin"
      :class="{ selected: selectedId === spot.id, disabled: spot.status === 'disabled' }"
      :style="{ left: `${Number(spot.map_x) * 100}%`, top: `${Number(spot.map_y) * 100}%` }"
      :title="spot.name"
      @click="$emit('select', spot)"
    ><span>{{ spot.name }}</span></button>
  </div>
</template>

<style scoped>
.map-panel { position: relative; min-height: 460px; overflow: hidden; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #e8eee9; box-shadow: var(--tw-shadow-card); }
.map-panel > img { width: 100%; height: 100%; min-height: 460px; display: block; object-fit: cover; }
.map-placeholder { min-height: 460px; display: grid; place-items: center; align-content: center; gap: 8px; background: radial-gradient(circle at 50% 40%, #f7fbf8, #dfe9e3); color: var(--tw-color-muted); }
.map-placeholder strong { color: var(--tw-color-text); }
.spot-pin { position: absolute; width: 18px; height: 18px; padding: 0; transform: translate(-50%, -50%); border: 3px solid #fff; border-radius: 50%; background: var(--tw-color-primary); box-shadow: 0 3px 10px rgb(24 60 50 / 30%); }
.spot-pin span { position: absolute; left: 50%; bottom: 20px; width: max-content; max-width: 140px; padding: 4px 7px; transform: translateX(-50%); border-radius: 6px; background: rgb(23 63 53 / 90%); color: #fff; font-size: 10px; opacity: 0; pointer-events: none; }
.spot-pin:hover span, .spot-pin:focus-visible span, .spot-pin.selected span { opacity: 1; }
.spot-pin.selected { background: var(--tw-color-accent); }
.spot-pin.disabled { background: #929e99; }
</style>
