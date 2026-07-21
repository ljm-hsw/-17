import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import PageState from '../feedback/PageState.vue'
import ConfirmReasonDialog from '../security/ConfirmReasonDialog.vue'
import OneTimeSecretDialog from '../security/OneTimeSecretDialog.vue'

const dialogStubs = { teleport: true }

describe('shared management components', () => {
  it('renders an error separately from empty data and exposes request id', () => {
    const wrapper = mount(PageState, {
      props: {
        status: 'error',
        title: '点位加载失败',
        description: '请检查网络后重试',
        requestId: 'req-spots',
      },
    })

    expect(wrapper.text()).toContain('点位加载失败')
    expect(wrapper.text()).toContain('req-spots')
    expect(wrapper.find('[data-test="empty-state"]').exists()).toBe(false)
  })

  it('requires a reason before confirming a risk action', async () => {
    const wrapper = mount(ConfirmReasonDialog, {
      props: { modelValue: false, title: '强制解绑' },
      global: { stubs: dialogStubs },
    })
    await wrapper.setProps({ modelValue: true })
    await flushPromises()

    await wrapper.get('[data-test="confirm-risk"]').trigger('click')
    expect(wrapper.emitted('confirm')).toBeUndefined()
    expect(wrapper.text()).toContain('必须填写操作原因')

    await wrapper.get('[data-test="risk-reason"]').setValue(' 用户报告卡片遗失 ')
    await wrapper.get('[data-test="confirm-risk"]').trigger('click')
    expect(wrapper.emitted('confirm')).toEqual([
      [{ confirm: true, reason: '用户报告卡片遗失' }],
    ])
  })

  it('requires acknowledgement before closing a one-time secret', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.assign(navigator, { clipboard: { writeText } })
    const wrapper = mount(OneTimeSecretDialog, {
      props: {
        modelValue: false,
        label: '设备密钥',
        secret: 'one-time-device-secret',
      },
      global: { stubs: dialogStubs },
    })
    await wrapper.setProps({ modelValue: true })
    await flushPromises()

    await wrapper.get('[data-test="copy-secret"]').trigger('click')
    expect(writeText).toHaveBeenCalledWith('one-time-device-secret')
    expect(wrapper.get('[data-test="close-secret"]').attributes('disabled')).toBeDefined()

    await wrapper.get('[data-test="secret-saved"]').setValue(true)
    await wrapper.get('[data-test="close-secret"]').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([[false]])
    expect(wrapper.emitted('closed')).toHaveLength(1)
  })
})
