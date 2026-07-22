<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElDialog } from 'element-plus'

import { confirmCardImport, previewCardImport } from '../../services/management/cards'
import type { CardImportRow, ImportPreview } from '../../types/card'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; imported: [] }>()
const rawRows = ref('')
const rows = ref<CardImportRow[]>([])
const preview = ref<ImportPreview | null>(null)
const confirmed = ref(false)
const loading = ref(false)
const error = ref('')
const cleanPreview = computed(() => Boolean(preview.value && preview.value.valid.length > 0 && preview.value.duplicate.length === 0 && preview.value.invalid.length === 0))

watch(() => props.modelValue, (visible) => { if (visible) { rawRows.value = ''; rows.value = []; preview.value = null; confirmed.value = false; error.value = '' } })
function parseRows() {
  return rawRows.value.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).map((line) => {
    const [serial_no = '', card_uid = ''] = line.split(',').map((value) => value.trim())
    return { serial_no, card_uid }
  })
}
async function runPreview() {
  rows.value = parseRows(); error.value = ''; confirmed.value = false
  if (rows.value.length === 0) { error.value = '请至少输入一行卡片数据'; return }
  loading.value = true
  try { preview.value = (await previewCardImport(rows.value)).data }
  catch (reason) { error.value = reason instanceof Error ? reason.message : '预检失败' }
  finally { loading.value = false }
}
async function confirmImport() {
  if (!cleanPreview.value || !confirmed.value) return
  loading.value = true
  try { await confirmCardImport(rows.value); emit('imported'); emit('update:modelValue', false) }
  catch (reason) { error.value = reason instanceof Error ? reason.message : '导入失败' }
  finally { loading.value = false }
}
</script>

<template>
  <ElDialog :model-value="modelValue" title="批量导入卡片" width="min(760px, calc(100vw - 32px))" :close-on-click-modal="!loading" @close="emit('update:modelValue', false)">
    <p class="hint">每行格式：<code>卡片编号,卡片UID</code>。UID 仅发送给后端生成摘要，预检结果不会返回原始 UID。</p>
    <textarea v-model="rawRows" data-test="import-rows" rows="8" placeholder="SCU-JA-0001,04A1B2C3D4&#10;SCU-JA-0002,04E5F6A7B8" />
    <button data-test="preview-import" type="button" class="secondary" :disabled="loading" @click="runPreview">{{ loading ? '正在处理…' : '预检数据' }}</button>
    <section v-if="preview" class="preview-grid"><article class="valid"><strong>{{ preview.valid.length }}</strong><span>可导入</span></article><article class="duplicate"><strong>{{ preview.duplicate.length }}</strong><span>重复</span></article><article class="invalid"><strong>{{ preview.invalid.length }}</strong><span>格式错误</span></article></section>
    <ul v-if="preview && !cleanPreview"><li v-for="row in [...preview.duplicate, ...preview.invalid]" :key="`${row.index}-${row.serial_no}`">第 {{ row.index + 1 }} 行 · {{ row.serial_no || '编号为空' }} · {{ row.reason || '数据重复' }}</li></ul>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <label class="confirm"><input v-model="confirmed" type="checkbox" :disabled="!cleanPreview" />我已核对预检结果，确认导入以上 {{ preview?.valid.length ?? 0 }} 张卡片</label>
    <template #footer><button type="button" class="secondary" :disabled="loading" @click="emit('update:modelValue', false)">取消</button><button data-test="confirm-import" type="button" :disabled="!cleanPreview || !confirmed || loading" @click="confirmImport">确认导入</button></template>
  </ElDialog>
</template>

<style scoped>
.hint { color: var(--tw-color-muted); line-height: 1.6; }.hint code { color: var(--tw-color-primary); }
textarea { width: 100%; padding: 12px; resize: vertical; border: 1px solid var(--tw-color-border); border-radius: var(--tw-radius-sm); font: 13px/1.7 ui-monospace, monospace; }
button { min-height: 40px; padding: 0 14px; border: 0; border-radius: var(--tw-radius-sm); background: var(--tw-color-primary); color: #fff; font-weight: 700; }.secondary { border: 1px solid var(--tw-color-border); background: #fff; color: var(--tw-color-primary); }
.preview-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 9px; margin-top: 14px; }.preview-grid article { display: grid; gap: 3px; padding: 13px; border-radius: var(--tw-radius-sm); background: #f4f7f5; }.preview-grid strong { font-size: 22px; }.preview-grid span { color: var(--tw-color-muted); font-size: 10px; }.duplicate strong, .invalid strong { color: var(--tw-color-danger); }
ul { max-height: 120px; overflow: auto; padding-left: 22px; color: var(--tw-color-danger); font-size: 11px; }.error { color: var(--tw-color-danger); }.confirm { display: flex; align-items: center; gap: 8px; margin-top: 16px; font-size: 12px; }
</style>
