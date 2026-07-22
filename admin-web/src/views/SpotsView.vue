<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElDrawer } from 'element-plus'

import PageState from '../components/feedback/PageState.vue'
import ConfirmReasonDialog from '../components/security/ConfirmReasonDialog.vue'
import SpotFormDrawer from '../features/content/SpotFormDrawer.vue'
import SpotMediaList from '../features/content/SpotMediaList.vue'
import {
  createSpot, createSpotMedia, disableSpot, disableSpotMedia,
  listSpots, publishSpot, updateSpot,
} from '../services/management/content'
import { useAuthStore } from '../stores/auth'
import { useDisplayStore } from '../stores/display'
import { useSceneStore } from '../stores/scene'
import type { Spot, SpotMedia, SpotPayload } from '../types/content'

const auth = useAuthStore()
const display = useDisplayStore()
const sceneStore = useSceneStore()
const items = ref<Spot[]>([])
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const search = ref('')
const status = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const formOpen = ref(false)
const editing = ref<Spot | null>(null)
const mediaSpot = ref<Spot | null>(null)
const disableTarget = ref<Spot | null>(null)
const mediaDisableTarget = ref<SpotMedia | null>(null)

const canEdit = computed(() => !display.isDemoMode && auth.can('scenes.change_spot'))
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const statusLabel = (value: string) => ({ draft: '草稿', published: '已发布', disabled: '已停用' })[value] ?? value
const categoryLabel = (value: string) => ({ landmark: '标志景观', checkin: '普通打卡', photo: '拍照打卡', study: '学习空间', service: '生活服务' })[value] ?? value

async function load() {
  if (!sceneStore.currentSceneId) { loading.value = false; return }
  loading.value = true
  error.value = ''
  try {
    const response = await listSpots({ sceneId: sceneStore.currentSceneId, search: search.value, status: status.value, page: page.value, pageSize })
    items.value = response.data.items
    total.value = response.meta?.total ?? items.value.length
    if (mediaSpot.value) mediaSpot.value = items.value.find((item) => item.id === mediaSpot.value?.id) ?? null
  } catch (reason) { error.value = reason instanceof Error ? reason.message : '点位加载失败' }
  finally { loading.value = false }
}

onMounted(load)
watch(() => sceneStore.currentSceneId, () => { page.value = 1; void load() })

function openCreate() { editing.value = null; formOpen.value = true }
function openEdit(spot: Spot) { editing.value = spot; formOpen.value = true }
async function save(payload: SpotPayload) {
  submitting.value = true
  try {
    if (editing.value) await updateSpot(editing.value.id, payload)
    else await createSpot(payload)
    formOpen.value = false
    await load()
  } catch (reason) { error.value = reason instanceof Error ? reason.message : '点位保存失败' }
  finally { submitting.value = false }
}
async function publish(spot: Spot) { submitting.value = true; try { await publishSpot(spot.id); await load() } finally { submitting.value = false } }
async function confirmDisable(payload: { confirm: true; reason: string }) {
  if (!disableTarget.value) return
  submitting.value = true
  try { await disableSpot(disableTarget.value.id, payload); disableTarget.value = null; await load() }
  finally { submitting.value = false }
}
async function addMedia(payload: Parameters<typeof createSpotMedia>[1]) {
  if (!mediaSpot.value) return
  submitting.value = true
  try { await createSpotMedia(mediaSpot.value.id, payload); await load() }
  finally { submitting.value = false }
}
async function confirmMediaDisable(payload: { confirm: true; reason: string }) {
  if (!mediaSpot.value || !mediaDisableTarget.value) return
  submitting.value = true
  try { await disableSpotMedia(mediaSpot.value.id, mediaDisableTarget.value.id, payload); mediaDisableTarget.value = null; await load() }
  finally { submitting.value = false }
}
</script>

<template>
  <div class="management-page">
    <header class="page-title"><div><p>CONTENT OPERATIONS</p><h1>点位管理</h1><span>维护地图坐标、导览内容、打卡策略与媒体资料</span></div><button v-if="canEdit" type="button" @click="openCreate">新建点位</button></header>
    <section class="filters">
      <label>搜索<input v-model.trim="search" placeholder="点位名称或英文标识" @keyup.enter="page = 1; load()" /></label>
      <label>状态<select v-model="status" @change="page = 1; load()"><option value="">全部状态</option><option value="draft">草稿</option><option value="published">已发布</option><option value="disabled">已停用</option></select></label>
      <button type="button" class="secondary" @click="page = 1; load()">查询</button>
    </section>
    <PageState v-if="loading && items.length === 0" status="loading" title="正在加载点位" />
    <PageState v-else-if="error" status="error" :description="error" @retry="load" />
    <PageState v-else-if="items.length === 0" status="empty" title="暂无符合条件的点位" />
    <section v-else class="table-card">
      <div class="table-scroll"><table><thead><tr><th>点位</th><th>分类</th><th>地图坐标</th><th>停留</th><th>状态</th><th>打卡</th><th>操作</th></tr></thead><tbody><tr v-for="spot in items" :key="spot.id"><td><strong>{{ spot.name }}</strong><small>{{ spot.slug }}</small></td><td>{{ categoryLabel(spot.category) }}</td><td>{{ spot.map_x }}, {{ spot.map_y }}</td><td>{{ spot.suggested_stay_minutes }} 分钟</td><td><span class="status" :class="`status--${spot.status}`">{{ statusLabel(spot.status) }}</span></td><td>{{ spot.is_checkin_enabled ? '开启' : '关闭' }}</td><td><div class="actions"><button type="button" class="link" @click="mediaSpot = spot">媒体</button><button v-if="canEdit" type="button" class="link" @click="openEdit(spot)">编辑</button><button v-if="canEdit && spot.status === 'draft'" type="button" class="link" @click="publish(spot)">发布</button><button v-if="canEdit && spot.status !== 'disabled'" data-test="disable-spot" type="button" class="danger-link" @click="disableTarget = spot">停用</button></div></td></tr></tbody></table></div>
      <footer class="pagination"><span>共 {{ total }} 条</span><button type="button" :disabled="page <= 1" @click="page--; load()">上一页</button><strong>{{ page }} / {{ totalPages }}</strong><button type="button" :disabled="page >= totalPages" @click="page++; load()">下一页</button></footer>
    </section>

    <SpotFormDrawer v-model="formOpen" :scene-id="sceneStore.currentSceneId" :spot="editing" :submitting="submitting" @submit="save" />
    <ElDrawer :model-value="Boolean(mediaSpot)" title="点位媒体资料" size="min(760px, 94vw)" @close="mediaSpot = null"><SpotMediaList v-if="mediaSpot" :spot="mediaSpot" :can-edit="canEdit" :submitting="submitting" @create="addMedia" @disable="mediaDisableTarget = $event" /></ElDrawer>
    <ConfirmReasonDialog :model-value="Boolean(disableTarget)" title="停用点位" description="停用后小程序不应再展示或接受该点位打卡，请填写操作原因。" :submitting="submitting" @update:model-value="!$event && (disableTarget = null)" @confirm="confirmDisable" />
    <ConfirmReasonDialog :model-value="Boolean(mediaDisableTarget)" title="停用媒体" :submitting="submitting" @update:model-value="!$event && (mediaDisableTarget = null)" @confirm="confirmMediaDisable" />
  </div>
</template>

<style scoped>
.management-page { max-width: 1540px; margin: 0 auto; padding: 26px; }
.page-title { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 20px; }
.page-title p, .page-title h1, .page-title span { margin: 0; }
.page-title p { color: var(--tw-color-accent); font-size: 10px; font-weight: 800; letter-spacing: .15em; }
.page-title h1 { margin: 4px 0 6px; font-size: 28px; }
.page-title span { color: var(--tw-color-muted); font-size: 12px; }
button { min-height: 40px; padding: 0 14px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }
.filters { display: flex; align-items: flex-end; gap: 10px; margin-bottom: 14px; padding: 14px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; }
.filters label { display: grid; gap: 5px; color: var(--tw-color-muted); font-size: 10px; }
.filters input, .filters select { min-height: 40px; min-width: 180px; padding: 8px 10px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); }
.filters input { min-width: 260px; }
.secondary { border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-primary); }
.table-card { overflow: hidden; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; box-shadow: var(--tw-shadow-card); }
.table-scroll { overflow-x: auto; }
table { width: 100%; min-width: 920px; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid #edf1ef; text-align: left; font-size: 12px; }
th { background: #f7f9f7; color: var(--tw-color-muted); font-size: 10px; letter-spacing: .05em; }
td:first-child { display: grid; gap: 3px; }
td small { color: var(--tw-color-muted); }
.status { padding: 4px 8px; border-radius: 999px; background: #f0f2f1; font-size: 10px; }
.status--published { background: var(--tw-color-primary-soft); color: var(--tw-color-primary); }
.status--disabled { background: #fff0ed; color: var(--tw-color-danger); }
.actions { display: flex; gap: 4px; }
.link, .danger-link { min-height: 34px; padding: 0 5px; background: transparent; color: var(--tw-color-primary); font-size: 11px; }
.danger-link { color: var(--tw-color-danger); }
.pagination { display: flex; align-items: center; justify-content: flex-end; gap: 10px; padding: 12px 16px; color: var(--tw-color-muted); font-size: 11px; }
.pagination span { margin-right: auto; }
.pagination button { min-height: 34px; border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-primary); }
@media (max-width: 700px) { .management-page { padding: 18px 14px; } .page-title { align-items: flex-start; flex-direction: column; } .filters { align-items: stretch; flex-direction: column; } .filters input, .filters select { width: 100%; min-width: 0; } }
</style>
