<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElDrawer } from 'element-plus'

import type { RoutePayload, Spot, TravelRoute } from '../../types/content'

const props = withDefaults(defineProps<{
  modelValue: boolean
  sceneId: string
  spots: Spot[]
  route?: TravelRoute | null
  submitting?: boolean
}>(), { route: null, submitting: false })
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; submit: [payload: RoutePayload] }>()

const errorMessage = ref('')
const form = reactive<RoutePayload>({ scene_id: '', slug: '', name: '', summary: '', estimated_minutes: 90, status: 'draft', stops: [] })
const availableSpots = computed(() => props.spots.filter((spot) => !form.stops.some((stop) => stop.spot_id === spot.id)))

function reset() {
  const source = props.route
  Object.assign(form, source ? {
    scene_id: source.scene_id, slug: source.slug, name: source.name, summary: source.summary ?? '',
    estimated_minutes: source.estimated_minutes, status: source.status,
    stops: source.stops.map((stop) => ({ ...stop })),
  } : { scene_id: props.sceneId, slug: '', name: '', summary: '', estimated_minutes: 90, status: 'draft', stops: [] })
  errorMessage.value = ''
}
watch(() => props.modelValue, (visible) => { if (visible) reset() })

function addStop(spotId: string) {
  if (!spotId || form.stops.some((stop) => stop.spot_id === spotId)) return
  form.stops.push({ spot_id: spotId, order: form.stops.length + 1, note: '' })
}
function move(index: number, offset: number) {
  const target = index + offset
  if (target < 0 || target >= form.stops.length) return
  const [row] = form.stops.splice(index, 1)
  if (row) form.stops.splice(target, 0, row)
}
function submit() {
  const ids = form.stops.map((stop) => stop.spot_id)
  if (!form.name.trim() || !form.slug.trim()) { errorMessage.value = '路线名称和英文标识不能为空'; return }
  if (ids.length === 0) { errorMessage.value = '路线至少需要一个点位'; return }
  if (new Set(ids).size !== ids.length) { errorMessage.value = '同一路线不能重复添加点位'; return }
  errorMessage.value = ''
  emit('submit', { ...form, stops: form.stops.map((stop, index) => ({ ...stop, order: index + 1 })) })
}
const spotName = (id: string) => props.spots.find((spot) => spot.id === id)?.name ?? '未知点位'
</script>

<template>
  <ElDrawer :model-value="modelValue" :title="route ? '编辑路线' : '新建路线'" size="min(680px, 94vw)" @close="emit('update:modelValue', false)">
    <form class="route-form" @submit.prevent="submit">
      <div class="form-grid">
        <label><span>路线名称 *</span><input v-model.trim="form.name" /></label>
        <label><span>英文标识 *</span><input v-model.trim="form.slug" /></label>
        <label><span>预计时长（分钟）</span><input v-model.number="form.estimated_minutes" type="number" min="1" /></label>
        <label><span>状态</span><select v-model="form.status"><option value="draft">草稿</option><option value="published">已发布</option><option value="disabled">已停用</option></select></label>
      </div>
      <label><span>路线简介</span><textarea v-model="form.summary" rows="3" maxlength="300" /></label>
      <section class="stops">
        <header><div><h3>路线点位</h3><p>拖动替代操作：使用上移、下移调整游览顺序。</p></div><select :value="''" @change="addStop(($event.target as HTMLSelectElement).value)"><option value="">添加点位…</option><option v-for="spot in availableSpots" :key="spot.id" :value="spot.id">{{ spot.name }}</option></select></header>
        <ol>
          <li v-for="(stop, index) in form.stops" :key="stop.spot_id">
            <strong>{{ index + 1 }}</strong><span>{{ spotName(stop.spot_id) }}</span>
            <input v-model="stop.note" aria-label="路线备注" placeholder="到访提示（可选）" />
            <button type="button" aria-label="上移" :disabled="index === 0" @click="move(index, -1)">↑</button>
            <button type="button" aria-label="下移" :disabled="index === form.stops.length - 1" @click="move(index, 1)">↓</button>
            <button type="button" class="remove" aria-label="删除点位" @click="form.stops.splice(index, 1)">×</button>
          </li>
        </ol>
      </section>
      <p v-if="errorMessage" class="form-error" role="alert">{{ errorMessage }}</p>
      <footer><button type="button" class="secondary" @click="emit('update:modelValue', false)">取消</button><button type="submit" :disabled="submitting || form.stops.length === 0">{{ submitting ? '正在保存…' : '保存路线' }}</button></footer>
    </form>
  </ElDrawer>
</template>

<style scoped>
.route-form { display: grid; gap: 17px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
label { display: grid; gap: 7px; font-size: 13px; font-weight: 700; }
input, select, textarea { min-width: 0; min-height: 42px; padding: 9px 11px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); background: #fff; color: var(--tw-color-text); font: inherit; font-weight: 400; }
.stops { padding-top: 8px; border-top: 1px solid var(--tw-color-border); }
.stops header { display: flex; align-items: end; justify-content: space-between; gap: 14px; }
h3, p { margin: 0; }
h3 { font-size: 15px; }
.stops p { margin-top: 4px; color: var(--tw-color-muted); font-size: 11px; }
ol { display: grid; gap: 8px; margin: 14px 0 0; padding: 0; list-style: none; }
li { display: grid; grid-template-columns: 28px minmax(100px, .8fr) minmax(120px, 1.5fr) 36px 36px 36px; align-items: center; gap: 7px; padding: 9px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); }
li > strong { width: 27px; height: 27px; display: grid; place-items: center; border-radius: 8px; background: var(--tw-color-primary-soft); color: var(--tw-color-primary); }
li button { min-height: 36px; padding: 0; }
.remove { background: #fff2ef; color: var(--tw-color-danger); }
.form-error { color: var(--tw-color-danger); font-size: 13px; }
footer { position: sticky; bottom: 0; display: flex; justify-content: flex-end; gap: 10px; padding: 14px 0 2px; background: #fff; }
button { min-height: 42px; padding: 0 18px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }
.secondary { border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-text); }
@media (max-width: 600px) { .form-grid { grid-template-columns: 1fr; } li { grid-template-columns: 28px 1fr 36px 36px 36px; } li input { grid-column: 2 / -1; grid-row: 2; } }
</style>
