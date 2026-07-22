<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import PageState from '../components/feedback/PageState.vue'
import SceneMapPanel from '../features/content/SceneMapPanel.vue'
import { listSpots, updateScene } from '../services/management/content'
import { useAuthStore } from '../stores/auth'
import { useDisplayStore } from '../stores/display'
import { useSceneStore } from '../stores/scene'
import type { Scene, Spot } from '../types/content'

const auth = useAuthStore()
const display = useDisplayStore()
const sceneStore = useSceneStore()
const spots = ref<Spot[]>([])
const selected = ref<Spot | null>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const canEdit = computed(() => !display.isDemoMode && auth.can('scenes.change_scene'))
const form = reactive({ name: '', slug: '', subtitle: '', timezone: 'Asia/Shanghai', map_image_url: '', status: 'draft' })

function syncForm(scene: Scene | null) {
  if (!scene) return
  Object.assign(form, { name: scene.name, slug: scene.slug, subtitle: scene.subtitle, timezone: scene.timezone, map_image_url: scene.map_image_url, status: scene.status })
}

async function load() {
  if (!sceneStore.currentSceneId) { loading.value = false; return }
  loading.value = true; error.value = ''
  try { spots.value = (await listSpots({ sceneId: sceneStore.currentSceneId, pageSize: 100 })).data.items; syncForm(sceneStore.currentScene) }
  catch (reason) { error.value = reason instanceof Error ? reason.message : '场景地图加载失败' }
  finally { loading.value = false }
}
onMounted(load)
watch(() => sceneStore.currentSceneId, () => { selected.value = null; void load() })

async function saveScene() {
  const scene = sceneStore.currentScene
  if (!scene) return
  saving.value = true
  try {
    const response = await updateScene(scene.id, { ...form })
    const index = sceneStore.scenes.findIndex((item) => item.id === scene.id)
    if (index >= 0) sceneStore.scenes[index] = response.data
    syncForm(response.data)
  } catch (reason) { error.value = reason instanceof Error ? reason.message : '场景保存失败' }
  finally { saving.value = false }
}
</script>

<template>
  <div class="scene-page">
    <header class="page-title"><div><p>CONTENT OPERATIONS</p><h1>场景与地图</h1><span>统一维护校区地图底图与点位空间分布</span></div></header>
    <PageState v-if="loading" status="loading" title="正在加载场景地图" />
    <PageState v-else-if="error && !sceneStore.currentScene" status="error" :description="error" @retry="load" />
    <PageState v-else-if="!sceneStore.currentScene" status="empty" title="暂无可运营场景" />
    <template v-else>
      <section class="scene-grid">
        <SceneMapPanel :scene="sceneStore.currentScene" :spots="spots" :selected-id="selected?.id" @select="selected = $event" />
        <aside class="scene-panel">
          <div><p class="eyebrow">SCENE SETTINGS</p><h2>{{ sceneStore.currentScene.name }}</h2><span>{{ spots.length }} 个点位</span></div>
          <form @submit.prevent="saveScene">
            <label>场景名称<input v-model.trim="form.name" :disabled="!canEdit" /></label>
            <label>英文标识<input v-model.trim="form.slug" :disabled="!canEdit" /></label>
            <label>副标题<input v-model.trim="form.subtitle" :disabled="!canEdit" /></label>
            <label>时区<input v-model.trim="form.timezone" :disabled="!canEdit" /></label>
            <label>地图图片 URL<input v-model.trim="form.map_image_url" type="url" :disabled="!canEdit" /></label>
            <label>状态<select v-model="form.status" :disabled="!canEdit"><option value="draft">草稿</option><option value="published">已发布</option><option value="disabled">已停用</option></select></label>
            <button v-if="canEdit" type="submit" :disabled="saving">{{ saving ? '正在保存…' : '保存场景设置' }}</button>
          </form>
          <section v-if="selected" class="selected-spot"><small>当前选中点位</small><strong>{{ selected.name }}</strong><span>{{ selected.map_x }}, {{ selected.map_y }} · {{ selected.status }}</span></section>
        </aside>
      </section>
      <p v-if="error" class="inline-error" role="alert">{{ error }}</p>
    </template>
  </div>
</template>

<style scoped>
.scene-page { max-width: 1540px; margin: 0 auto; padding: 26px; }
.page-title { margin-bottom: 20px; }
.page-title p, .page-title h1, .page-title span { margin: 0; }
.page-title p, .eyebrow { color: var(--tw-color-accent); font-size: 10px; font-weight: 800; letter-spacing: .15em; }
.page-title h1 { margin: 4px 0 6px; font-size: 28px; }
.page-title span { color: var(--tw-color-muted); font-size: 12px; }
.scene-grid { display: grid; grid-template-columns: minmax(0, 1.7fr) minmax(310px, .7fr); gap: 14px; }
.scene-panel { padding: 22px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-md); background: #fff; box-shadow: var(--tw-shadow-card); }
.scene-panel h2, .scene-panel p { margin: 0; }
.scene-panel h2 { margin: 5px 0; font-size: 19px; }
.scene-panel > div > span { color: var(--tw-color-muted); font-size: 11px; }
form { display: grid; gap: 11px; margin-top: 20px; }
label { display: grid; gap: 5px; color: var(--tw-color-muted); font-size: 10px; }
input, select { min-height: 40px; width: 100%; padding: 8px 10px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); background: #fff; color: var(--tw-color-text); }
button { min-height: 42px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }
.selected-spot { display: grid; gap: 4px; margin-top: 18px; padding: 13px; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary-soft); }
.selected-spot small, .selected-spot span { color: var(--tw-color-muted); font-size: 10px; }
.inline-error { color: var(--tw-color-danger); }
@media (max-width: 980px) { .scene-grid { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .scene-page { padding: 18px 14px; } }
</style>
