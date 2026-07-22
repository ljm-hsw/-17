<script setup lang="ts">
import { reactive, ref } from 'vue'

import type { Spot, SpotMedia } from '../../types/content'

defineProps<{ spot: Spot; canEdit: boolean; submitting?: boolean }>()
const emit = defineEmits<{
  create: [payload: { url: string; storage_key: string; media_type: 'image'; caption: string; sort_order: number; status: 'draft' }]
  disable: [media: SpotMedia]
}>()

const adding = ref(false)
const form = reactive({ url: '', storage_key: '', caption: '', sort_order: 0 })

function submit() {
  if (!form.url.trim() && !form.storage_key.trim()) return
  emit('create', { ...form, media_type: 'image', status: 'draft' })
  Object.assign(form, { url: '', storage_key: '', caption: '', sort_order: 0 })
  adding.value = false
}
</script>

<template>
  <section class="media-section">
    <header><div><h3>点位媒体</h3><p>当前接口仅登记图片 URL 或存储键，不上传二进制文件。</p></div><button v-if="canEdit" type="button" class="secondary" @click="adding = !adding">{{ adding ? '收起' : '添加图片' }}</button></header>
    <form v-if="adding" class="media-form" @submit.prevent="submit">
      <input v-model.trim="form.url" type="url" placeholder="图片 URL" />
      <input v-model.trim="form.storage_key" placeholder="对象存储键（可选）" />
      <input v-model.trim="form.caption" placeholder="图片说明" />
      <input v-model.number="form.sort_order" type="number" min="0" placeholder="排序" />
      <button type="submit" :disabled="submitting">保存图片信息</button>
    </form>
    <p v-if="spot.media.length === 0" class="empty">暂无媒体资料</p>
    <ul v-else>
      <li v-for="media in spot.media" :key="media.id">
        <img v-if="media.url" :src="media.url" :alt="media.caption || `${spot.name}图片`" loading="lazy" />
        <span><strong>{{ media.caption || '未命名图片' }}</strong><small>{{ media.url || media.storage_key }}</small></span>
        <em>{{ media.status }}</em>
        <button v-if="canEdit && media.status !== 'disabled'" type="button" class="danger-link" @click="emit('disable', media)">停用</button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.media-section { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--tw-color-border); }
header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
h3, p { margin: 0; }
h3 { font-size: 15px; }
header p, .empty { margin-top: 4px; color: var(--tw-color-muted); font-size: 11px; }
.media-form { display: grid; grid-template-columns: 2fr 1.5fr 1.5fr 80px auto; gap: 8px; margin: 14px 0; }
input { min-width: 0; min-height: 40px; padding: 8px 10px; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); }
button { min-height: 40px; padding: 0 12px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }
.secondary { border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-primary); }
ul { margin: 14px 0 0; padding: 0; list-style: none; }
li { min-height: 64px; display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #eef2ef; }
li img { width: 62px; height: 48px; border-radius: 7px; object-fit: cover; }
li span { min-width: 0; display: grid; flex: 1; gap: 3px; }
li small { overflow: hidden; color: var(--tw-color-muted); font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
li em { color: var(--tw-color-muted); font-size: 10px; font-style: normal; }
.danger-link { min-height: 36px; padding: 0 6px; background: transparent; color: var(--tw-color-danger); }
@media (max-width: 720px) { .media-form { grid-template-columns: 1fr; } }
</style>
