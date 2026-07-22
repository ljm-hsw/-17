<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElDrawer } from 'element-plus'

import type { Scene, Spot } from '../../types/content'
import type { Device, DevicePayload } from '../../types/device'

const props = withDefaults(defineProps<{ modelValue: boolean; scenes: Scene[]; spots: Spot[]; device?: Device | null; submitting?: boolean }>(), { device: null, submitting: false })
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; submit: [payload: DevicePayload] }>()
const error = ref('')
const form = reactive<DevicePayload>({ device_id: '', scene_id: '', spot_id: '', device_type: 'rfid', status: 'active', firmware_version: '' })
const availableSpots = computed(() => props.spots.filter((spot) => spot.scene_id === form.scene_id))

function reset() {
  Object.assign(form, props.device ? {
    device_id: props.device.device_id, scene_id: props.device.scene_id, spot_id: props.device.spot_id,
    device_type: props.device.device_type, status: props.device.status, firmware_version: props.device.firmware_version,
  } : { device_id: '', scene_id: props.scenes[0]?.id ?? '', spot_id: '', device_type: 'rfid', status: 'active', firmware_version: '' })
  error.value = ''
}
watch(() => props.modelValue, (visible) => { if (visible) reset() })
function sceneChanged() { if (!availableSpots.value.some((spot) => spot.id === form.spot_id)) form.spot_id = '' }
function submit() {
  if (!form.device_id.trim() || !form.scene_id || !form.spot_id) { error.value = '设备编号、场景和点位不能为空'; return }
  error.value = ''; emit('submit', { ...form })
}
</script>

<template>
  <ElDrawer :model-value="modelValue" :title="device ? '编辑设备' : '接入设备'" size="min(560px, 94vw)" @close="emit('update:modelValue', false)">
    <form class="device-form" @submit.prevent="submit">
      <label>设备编号 *<input v-model.trim="form.device_id" placeholder="SCU-JA-DEVICE-001" /></label>
      <label>所属场景 *<select v-model="form.scene_id" data-test="device-scene" @change="sceneChanged"><option v-for="scene in scenes" :key="scene.id" :value="scene.id">{{ scene.name }}</option></select></label>
      <label>安装点位 *<select v-model="form.spot_id" data-test="device-spot"><option value="">请选择点位</option><option v-for="spot in availableSpots" :key="spot.id" :value="spot.id">{{ spot.name }}</option></select></label>
      <label>设备类型<select v-model="form.device_type"><option value="rfid">RFID</option><option value="nfc">NFC</option><option value="hybrid">RFID + NFC</option></select></label>
      <label>运行状态<select v-model="form.status"><option value="active">启用</option><option value="disabled">停用</option></select></label>
      <label>固件版本<input v-model.trim="form.firmware_version" placeholder="1.0.0" /></label>
      <p v-if="error" role="alert">{{ error }}</p>
      <footer><button type="button" class="secondary" @click="emit('update:modelValue', false)">取消</button><button type="submit" :disabled="submitting">{{ submitting ? '正在保存…' : '保存设备' }}</button></footer>
    </form>
  </ElDrawer>
</template>

<style scoped>
.device-form { display: grid; gap: 14px; }
label { display: grid; gap: 7px; font-size: 13px; font-weight: 700; }
input, select { min-height: 42px; padding: 9px 11px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); background: #fff; }
p { margin: 0; color: var(--tw-color-danger); }
footer { display: flex; justify-content: flex-end; gap: 9px; margin-top: 8px; }
button { min-height: 42px; padding: 0 17px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }
.secondary { border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-text); }
</style>
