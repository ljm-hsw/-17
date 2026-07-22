<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import PageState from '../components/feedback/PageState.vue'
import RouteFormDrawer from '../features/content/RouteFormDrawer.vue'
import { createRoute, listRoutes, listSpots, updateRoute } from '../services/management/content'
import { useAuthStore } from '../stores/auth'
import { useDisplayStore } from '../stores/display'
import { useSceneStore } from '../stores/scene'
import type { RoutePayload, Spot, TravelRoute } from '../types/content'

const auth = useAuthStore(); const display = useDisplayStore(); const sceneStore = useSceneStore()
const routes = ref<TravelRoute[]>([]); const spots = ref<Spot[]>([]); const loading = ref(true); const saving = ref(false); const error = ref('')
const search = ref(''); const status = ref(''); const formOpen = ref(false); const editing = ref<TravelRoute | null>(null)
const canEdit = computed(() => !display.isDemoMode && auth.can('scenes.change_route'))
const spotName = (id: string) => spots.value.find((spot) => spot.id === id)?.name ?? '未知点位'
const statusLabel = (value: string) => ({ draft: '草稿', published: '已发布', disabled: '已停用' })[value] ?? value

async function load() {
  if (!sceneStore.currentSceneId) { loading.value = false; return }
  loading.value = true; error.value = ''
  try {
    const [routeResponse, spotResponse] = await Promise.all([
      listRoutes({ sceneId: sceneStore.currentSceneId, search: search.value, status: status.value, pageSize: 100 }),
      listSpots({ sceneId: sceneStore.currentSceneId, pageSize: 100 }),
    ])
    routes.value = routeResponse.data.items; spots.value = spotResponse.data.items
  } catch (reason) { error.value = reason instanceof Error ? reason.message : '路线加载失败' }
  finally { loading.value = false }
}
onMounted(load); watch(() => sceneStore.currentSceneId, load)
function openCreate() { editing.value = null; formOpen.value = true }
function openEdit(route: TravelRoute) { editing.value = route; formOpen.value = true }
async function save(payload: RoutePayload) {
  saving.value = true
  try { if (editing.value) await updateRoute(editing.value.id, payload); else await createRoute(payload); formOpen.value = false; await load() }
  catch (reason) { error.value = reason instanceof Error ? reason.message : '路线保存失败' }
  finally { saving.value = false }
}
</script>

<template>
  <div class="route-page">
    <header class="page-title"><div><p>CONTENT OPERATIONS</p><h1>游览路线</h1><span>编排推荐游览顺序和每站到访提示</span></div><button v-if="canEdit" type="button" @click="openCreate">新建路线</button></header>
    <section class="filters"><input v-model.trim="search" placeholder="搜索路线名称" @keyup.enter="load" /><select v-model="status" @change="load"><option value="">全部状态</option><option value="draft">草稿</option><option value="published">已发布</option><option value="disabled">已停用</option></select><button class="secondary" type="button" @click="load">查询</button></section>
    <PageState v-if="loading && routes.length === 0" status="loading" title="正在加载路线" />
    <PageState v-else-if="error" status="error" :description="error" @retry="load" />
    <PageState v-else-if="routes.length === 0" status="empty" title="暂无符合条件的路线" />
    <section v-else class="route-grid">
      <article v-for="route in routes" :key="route.id">
        <header><div><span class="status">{{ statusLabel(route.status) }}</span><h2>{{ route.name }}</h2><p>{{ route.estimated_minutes }} 分钟 · {{ route.stops.length }} 个点位</p></div><button v-if="canEdit" type="button" class="link" @click="openEdit(route)">编辑</button></header>
        <ol><li v-for="(stop, index) in route.stops" :key="stop.spot_id"><strong>{{ index + 1 }}</strong><span>{{ spotName(stop.spot_id) }}<small v-if="stop.note">{{ stop.note }}</small></span></li></ol>
      </article>
    </section>
    <RouteFormDrawer v-model="formOpen" :scene-id="sceneStore.currentSceneId" :spots="spots" :route="editing" :submitting="saving" @submit="save" />
  </div>
</template>

<style scoped>
.route-page { max-width: 1540px; margin: 0 auto; padding: 26px; }
.page-title { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 20px; }
.page-title p, .page-title h1, .page-title span { margin: 0; }
.page-title p { color: var(--tw-color-accent); font-size: 10px; font-weight: 800; letter-spacing: .15em; }
.page-title h1 { margin: 4px 0 6px; font-size: 28px; }
.page-title span { color: var(--tw-color-muted); font-size: 12px; }
button { min-height: 40px; padding: 0 14px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }
.filters { display: flex; gap: 9px; margin-bottom: 14px; padding: 14px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; }
.filters input, .filters select { min-height: 40px; padding: 8px 10px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); }
.filters input { min-width: 260px; }
.secondary, .link { border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-primary); }
.route-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
article { padding: 20px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; box-shadow: var(--tw-shadow-card); }
article > header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
article h2, article p { margin: 0; }
article h2 { margin: 8px 0 4px; font-size: 18px; }
article p { color: var(--tw-color-muted); font-size: 11px; }
.status { padding: 4px 8px; border-radius: 999px; background: var(--tw-color-primary-soft); color: var(--tw-color-primary); font-size: 9px; }
ol { display: flex; align-items: flex-start; gap: 4px; margin: 20px 0 0; padding: 0; overflow-x: auto; list-style: none; }
li { min-width: 100px; position: relative; display: grid; justify-items: center; gap: 6px; color: var(--tw-color-muted); font-size: 10px; text-align: center; }
li:not(:last-child)::after { content: ''; position: absolute; top: 14px; left: calc(50% + 18px); width: calc(100% - 36px); border-top: 1px dashed #aac2b8; }
li strong { z-index: 1; width: 28px; height: 28px; display: grid; place-items: center; border-radius: 50%; background: var(--tw-color-primary); color: #fff; }
li span { display: grid; gap: 2px; }
li small { color: #879790; }
@media (max-width: 860px) { .route-grid { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .route-page { padding: 18px 14px; } .page-title { align-items: flex-start; flex-direction: column; } .filters { flex-direction: column; } .filters input { min-width: 0; } }
</style>
