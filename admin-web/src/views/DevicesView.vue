<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import PageState from '../components/feedback/PageState.vue'
import ConfirmReasonDialog from '../components/security/ConfirmReasonDialog.vue'
import OneTimeSecretDialog from '../components/security/OneTimeSecretDialog.vue'
import DeviceDetailDrawer from '../features/devices/DeviceDetailDrawer.vue'
import DeviceFormDrawer from '../features/devices/DeviceFormDrawer.vue'
import { listSpots } from '../services/management/content'
import { createDevice, listDeviceCheckins, listDevices, rotateDeviceSecret, updateDevice } from '../services/management/devices'
import { useAuthStore } from '../stores/auth'
import { useDisplayStore } from '../stores/display'
import { useSceneStore } from '../stores/scene'
import type { Spot } from '../types/content'
import type { CheckinEvent } from '../types/dashboard'
import type { Device, DevicePayload } from '../types/device'

const auth = useAuthStore(); const display = useDisplayStore(); const sceneStore = useSceneStore()
const devices = ref<Device[]>([]); const spots = ref<Spot[]>([]); const events = ref<CheckinEvent[]>([])
const loading = ref(true); const submitting = ref(false); const error = ref(''); const search = ref(''); const status = ref(''); const spotId = ref('')
const formOpen = ref(false); const editing = ref<Device | null>(null); const detail = ref<Device | null>(null); const rotateTarget = ref<Device | null>(null)
const oneTimeSecret = ref(''); const secretOpen = ref(false)
const canEdit = computed(() => !display.isDemoMode && auth.can('iot.change_device'))
const sceneSpots = computed(() => spots.value.filter((spot) => spot.scene_id === sceneStore.currentSceneId))
const spotName = (id: string) => spots.value.find((spot) => spot.id === id)?.name ?? '未知点位'
function isOnline(device: Device) { return device.status === 'active' && Boolean(device.last_seen_at) && Date.now() - new Date(device.last_seen_at!).getTime() <= 120_000 }

async function load() {
  if (!sceneStore.currentSceneId) { loading.value = false; return }
  loading.value = true; error.value = ''
  try {
    const [deviceResponse, spotResponse] = await Promise.all([listDevices({ sceneId: sceneStore.currentSceneId, spotId: spotId.value, status: status.value, search: search.value, pageSize: 100 }), listSpots({ sceneId: sceneStore.currentSceneId, pageSize: 100 })])
    devices.value = deviceResponse.data.items; spots.value = spotResponse.data.items
  } catch (reason) { error.value = reason instanceof Error ? reason.message : '设备加载失败' }
  finally { loading.value = false }
}
onMounted(load); watch(() => sceneStore.currentSceneId, () => { spotId.value = ''; void load() })
function openCreate() { editing.value = null; formOpen.value = true }
function openEdit(device: Device) { editing.value = device; formOpen.value = true }
async function save(payload: DevicePayload) {
  submitting.value = true
  try {
    if (editing.value) await updateDevice(editing.value.id, payload)
    else { const response = await createDevice(payload); oneTimeSecret.value = response.data.device_secret; secretOpen.value = true }
    formOpen.value = false; await load()
  } catch (reason) { error.value = reason instanceof Error ? reason.message : '设备保存失败' }
  finally { submitting.value = false }
}
async function openDetail(device: Device) { detail.value = device; try { events.value = (await listDeviceCheckins(device.id)).data.items } catch { events.value = [] } }
function askRotate(device = detail.value) { if (device) { rotateTarget.value = device; detail.value = null } }
async function confirmRotate(payload: { confirm: true; reason: string }) {
  if (!rotateTarget.value) return
  submitting.value = true
  try { const response = await rotateDeviceSecret(rotateTarget.value.id, payload); oneTimeSecret.value = response.data.device_secret; rotateTarget.value = null; secretOpen.value = true; await load() }
  finally { submitting.value = false }
}
</script>

<template>
  <div class="device-page">
    <header class="page-title"><div><p>IOT OPERATIONS</p><h1>设备管理</h1><span>查看在线心跳、固件状态并安全管理设备密钥</span></div><button v-if="canEdit" type="button" @click="openCreate">接入设备</button></header>
    <section class="filters"><input v-model.trim="search" placeholder="设备编号或固件版本" @keyup.enter="load" /><select v-model="spotId" @change="load"><option value="">全部点位</option><option v-for="spot in sceneSpots" :key="spot.id" :value="spot.id">{{ spot.name }}</option></select><select v-model="status" @change="load"><option value="">全部状态</option><option value="active">启用</option><option value="disabled">停用</option></select><button class="secondary" type="button" @click="load">查询</button></section>
    <PageState v-if="loading && devices.length === 0" status="loading" title="正在加载设备" />
    <PageState v-else-if="error" status="error" :description="error" @retry="load" />
    <PageState v-else-if="devices.length === 0" status="empty" title="暂无符合条件的设备" />
    <section v-else class="table-card"><div class="table-scroll"><table><thead><tr><th>设备</th><th>安装点位</th><th>类型</th><th>连接状态</th><th>固件</th><th>密钥指纹</th><th>操作</th></tr></thead><tbody><tr v-for="device in devices" :key="device.id"><td><strong>{{ device.device_id }}</strong><small>{{ device.last_error_code || '无错误' }}</small></td><td>{{ spotName(device.spot_id) }}</td><td>{{ device.device_type.toUpperCase() }}</td><td><span class="connection" :class="{ online: isOnline(device), disabled: device.status === 'disabled' }"><i />{{ device.status === 'disabled' ? '已停用' : isOnline(device) ? '在线' : '离线' }}</span></td><td>{{ device.firmware_version || '未知' }}</td><td><code>{{ device.secret_fingerprint }}</code></td><td><div class="actions"><button class="link" type="button" @click="openDetail(device)">详情</button><button v-if="canEdit" class="link" type="button" @click="openEdit(device)">编辑</button><button v-if="canEdit && device.status === 'active'" class="danger-link" type="button" @click="askRotate(device)">轮换密钥</button></div></td></tr></tbody></table></div></section>
    <DeviceFormDrawer v-model="formOpen" :scenes="sceneStore.scenes" :spots="spots" :device="editing" :submitting="submitting" @submit="save" />
    <DeviceDetailDrawer :model-value="Boolean(detail)" :device="detail" :events="events" :spot-name="detail ? spotName(detail.spot_id) : ''" @update:model-value="!$event && (detail = null)" @rotate="askRotate()" />
    <ConfirmReasonDialog :model-value="Boolean(rotateTarget)" title="轮换设备密钥" description="旧密钥会立即失效。请确保设备端可以同步更新，并填写轮换原因。" :submitting="submitting" @update:model-value="!$event && (rotateTarget = null)" @confirm="confirmRotate" />
    <OneTimeSecretDialog v-model="secretOpen" label="设备密钥" :secret="oneTimeSecret" @closed="oneTimeSecret = ''" />
  </div>
</template>

<style scoped>
.device-page { max-width: 1540px; margin: 0 auto; padding: 26px; }
.page-title { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 20px; }
.page-title p, .page-title h1, .page-title span { margin: 0; }.page-title p { color: var(--tw-color-accent); font-size: 10px; font-weight: 800; letter-spacing: .15em; }.page-title h1 { margin: 4px 0 6px; font-size: 28px; }.page-title span { color: var(--tw-color-muted); font-size: 12px; }
button { min-height: 40px; padding: 0 14px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }
.filters { display: flex; gap: 9px; margin-bottom: 14px; padding: 14px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; }.filters input, .filters select { min-height: 40px; padding: 8px 10px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); }.filters input { min-width: 250px; }.secondary { border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-primary); }
.table-card { overflow: hidden; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; box-shadow: var(--tw-shadow-card); }.table-scroll { overflow-x: auto; }table { width: 100%; min-width: 980px; border-collapse: collapse; }th, td { padding: 14px 15px; border-bottom: 1px solid #edf1ef; text-align: left; font-size: 12px; }th { background: #f7f9f7; color: var(--tw-color-muted); font-size: 10px; }td:first-child { display: grid; gap: 3px; }td small { color: var(--tw-color-muted); }code { font-size: 10px; }
.connection { display: inline-flex; align-items: center; gap: 6px; color: var(--tw-color-muted); }.connection i { width: 7px; height: 7px; border-radius: 50%; background: #aab5b0; }.connection.online { color: var(--tw-color-primary); }.connection.online i { background: #42a77f; }.connection.disabled { color: var(--tw-color-danger); }.connection.disabled i { background: var(--tw-color-danger); }
.actions { display: flex; gap: 3px; }.link, .danger-link { min-height: 34px; padding: 0 5px; background: transparent; color: var(--tw-color-primary); font-size: 11px; }.danger-link { color: var(--tw-color-danger); }
@media (max-width: 700px) { .device-page { padding: 18px 14px; }.page-title { align-items: flex-start; flex-direction: column; }.filters { flex-direction: column; }.filters input { min-width: 0; } }
</style>
