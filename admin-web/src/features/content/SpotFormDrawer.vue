<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElDrawer } from 'element-plus'

import type { Spot, SpotPayload } from '../../types/content'

const props = withDefaults(defineProps<{
  modelValue: boolean
  sceneId: string
  spot?: Spot | null
  submitting?: boolean
}>(), { spot: null, submitting: false })

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [payload: SpotPayload]
}>()

const errorMessage = ref('')
const tagText = ref('')
const form = reactive<SpotPayload>({
  scene_id: '', slug: '', name: '', category: 'checkin', summary: '', description: '',
  knowledge_content: '', map_x: '0.5', map_y: '0.5', tags: [],
  suggested_stay_minutes: 15, status: 'draft', is_checkin_enabled: true, is_photo_spot: false,
})

function reset() {
  const source = props.spot
  Object.assign(form, source ? {
    scene_id: source.scene_id, slug: source.slug, name: source.name, category: source.category,
    summary: source.summary, description: source.description,
    knowledge_content: source.knowledge_content, map_x: source.map_x, map_y: source.map_y,
    tags: [...source.tags], suggested_stay_minutes: source.suggested_stay_minutes,
    status: source.status, is_checkin_enabled: source.is_checkin_enabled,
    is_photo_spot: source.is_photo_spot,
  } : {
    scene_id: props.sceneId, slug: '', name: '', category: 'checkin', summary: '', description: '',
    knowledge_content: '', map_x: '0.5', map_y: '0.5', tags: [],
    suggested_stay_minutes: 15, status: 'draft', is_checkin_enabled: true, is_photo_spot: false,
  })
  tagText.value = form.tags.join('、')
  errorMessage.value = ''
}

watch(() => props.modelValue, (visible) => { if (visible) reset() })
watch(() => props.sceneId, (value) => { if (!props.spot) form.scene_id = value })

function submit() {
  const x = Number(form.map_x)
  const y = Number(form.map_y)
  if (!form.name.trim() || !form.slug.trim()) {
    errorMessage.value = '点位名称和英文标识不能为空'
    return
  }
  if (!Number.isFinite(x) || !Number.isFinite(y) || x < 0 || x > 1 || y < 0 || y > 1) {
    errorMessage.value = '地图坐标必须在 0 到 1 之间'
    return
  }
  errorMessage.value = ''
  form.tags = tagText.value.split(/[、,，]/).map((item) => item.trim()).filter(Boolean)
  emit('submit', { ...form, tags: [...form.tags], map_x: String(form.map_x), map_y: String(form.map_y) })
}
</script>

<template>
  <ElDrawer
    :model-value="modelValue"
    :title="spot ? '编辑点位' : '新建点位'"
    size="min(640px, 94vw)"
    :close-on-click-modal="!submitting"
    @close="emit('update:modelValue', false)"
  >
    <form class="content-form" @submit.prevent="submit">
      <div class="form-grid">
        <label><span>点位名称 *</span><input v-model.trim="form.name" data-test="spot-name" /></label>
        <label><span>英文标识 *</span><input v-model.trim="form.slug" placeholder="jiang-an-library" /></label>
        <label><span>点位分类</span><select v-model="form.category"><option value="landmark">标志景观</option><option value="checkin">普通打卡点</option><option value="photo">拍照打卡点</option><option value="study">学习空间</option><option value="service">生活服务</option></select></label>
        <label><span>发布状态</span><select v-model="form.status"><option value="draft">草稿</option><option value="published">已发布</option><option value="disabled">已停用</option></select></label>
        <label><span>横向坐标（0–1）</span><input v-model="form.map_x" inputmode="decimal" /></label>
        <label><span>纵向坐标（0–1）</span><input v-model="form.map_y" inputmode="decimal" /></label>
        <label><span>建议停留（分钟）</span><input v-model.number="form.suggested_stay_minutes" type="number" min="1" max="1440" /></label>
        <label><span>标签（顿号分隔）</span><input v-model="tagText" placeholder="学习、建筑" /></label>
      </div>
      <label><span>一句话简介</span><textarea v-model="form.summary" rows="2" maxlength="300" /></label>
      <label><span>详细介绍</span><textarea v-model="form.description" rows="4" /></label>
      <label><span>知识内容</span><textarea v-model="form.knowledge_content" rows="4" /></label>
      <div class="check-row">
        <label><input v-model="form.is_checkin_enabled" type="checkbox" />允许打卡</label>
        <label><input v-model="form.is_photo_spot" type="checkbox" />推荐拍照点</label>
      </div>
      <p v-if="errorMessage" class="form-error" role="alert">{{ errorMessage }}</p>
      <footer><button type="button" class="secondary" @click="emit('update:modelValue', false)">取消</button><button data-test="spot-submit" type="button" :disabled="submitting" @click="submit">{{ submitting ? '正在保存…' : '保存点位' }}</button></footer>
    </form>
  </ElDrawer>
</template>

<style scoped>
.content-form { display: grid; gap: 16px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
label { display: grid; gap: 7px; color: var(--tw-color-text); font-size: 13px; font-weight: 700; }
input, select, textarea { width: 100%; min-height: 42px; padding: 9px 11px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); background: #fff; color: var(--tw-color-text); font: inherit; font-weight: 400; }
textarea { resize: vertical; }
.check-row { display: flex; gap: 24px; }
.check-row label { display: flex; align-items: center; gap: 8px; }
.check-row input { width: 18px; min-height: 18px; }
.form-error { margin: 0; color: var(--tw-color-danger); font-size: 13px; }
footer { position: sticky; bottom: 0; display: flex; justify-content: flex-end; gap: 10px; padding: 14px 0 2px; background: #fff; }
button { min-height: 42px; padding: 0 18px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }
.secondary { border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-text); }
@media (max-width: 560px) { .form-grid { grid-template-columns: 1fr; } }
</style>
