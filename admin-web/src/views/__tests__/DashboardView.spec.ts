import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import DashboardView from '../DashboardView.vue'

describe('DashboardView', () => {
  afterEach(() => vi.restoreAllMocks())

  it('shows the backend health result', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ data: { status: 'ok' } }),
      }),
    )

    const wrapper = mount(DashboardView)
    await flushPromises()

    expect(wrapper.get('[data-test="backend-status"]').text()).toContain('正常')
  })
})
