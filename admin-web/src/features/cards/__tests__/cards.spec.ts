import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as cardApi from '../../../services/management/cards'
import { useAuthStore } from '../../../stores/auth'
import CardImportDialog from '../CardImportDialog.vue'
import CardsView from '../../../views/CardsView.vue'

describe('card operations', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    setActivePinia(createPinia())
    useAuthStore().$patch({ user: { id: 'admin', username: 'admin', nickname: '管理员', is_superuser: true, is_demo: false, permissions: [] } })
  })
  afterEach(() => { vi.restoreAllMocks(); document.body.innerHTML = '' })

  it('keeps import confirmation disabled when preview has duplicates or invalid rows', async () => {
    vi.spyOn(cardApi, 'previewCardImport').mockResolvedValue({
      data: {
        valid: [{ index: 0, serial_no: 'SCU-001', uid_masked: '****A1B2' }],
        duplicate: [{ index: 1, serial_no: 'SCU-002', uid_masked: '****C3D4' }],
        invalid: [{ index: 2, serial_no: 'SCU-003', reason: '格式不正确' }],
      },
      requestId: 'req-preview',
    })
    const wrapper = mount(CardImportDialog, { attachTo: document.body, props: { modelValue: false } })
    await wrapper.setProps({ modelValue: true }); await flushPromises()
    const textarea = document.body.querySelector('[data-test="import-rows"]') as HTMLTextAreaElement
    textarea.value = 'SCU-001,04A1B2\nSCU-002,04C3D4\nSCU-003,wrong'
    textarea.dispatchEvent(new Event('input', { bubbles: true }))
    ;(document.body.querySelector('[data-test="preview-import"]') as HTMLButtonElement).click()
    await flushPromises()

    expect((document.body.querySelector('[data-test="confirm-import"]') as HTMLButtonElement).disabled).toBe(true)
    wrapper.unmount()
  })

  it('shows an activation code once and clears it after acknowledged close', async () => {
    vi.spyOn(cardApi, 'listCards').mockResolvedValue({
      data: { items: [{ id: 'card-1', serial_no: 'SCU-JA-0001', uid_masked: '****A1B2', status: 'available', issued_at: null, last_used_at: null }] },
      meta: { page: 1, page_size: 20, total: 1 }, requestId: 'req-cards',
    })
    vi.spyOn(cardApi, 'createActivationCode').mockResolvedValue({
      data: { id: 'code-1', card_id: 'card-1', activation_code: 'ACT12345' }, requestId: 'req-code',
    })
    const wrapper = mount(CardsView, { attachTo: document.body })
    await flushPromises()
    await wrapper.get('[data-test="create-activation-code"]').trigger('click'); await flushPromises()
    expect(document.body.textContent).toContain('ACT12345')

    const saved = document.body.querySelector('[data-test="secret-saved"]') as HTMLInputElement
    saved.click(); await flushPromises()
    ;(document.body.querySelector('[data-test="close-secret"]') as HTMLButtonElement).click(); await flushPromises()
    expect(document.body.textContent).not.toContain('ACT12345')
    wrapper.unmount()
  })
})
