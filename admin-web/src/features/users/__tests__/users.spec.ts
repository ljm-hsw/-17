import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as http from '../../../services/http'
import * as userApi from '../../../services/management/users'
import { forceUnbind } from '../../../services/management/users'
import { useAuthStore } from '../../../stores/auth'
import UsersView from '../../../views/UsersView.vue'

describe('user operations', () => {
  beforeEach(() => { setActivePinia(createPinia()); useAuthStore().$patch({ user: { id: 'admin', username: 'admin', nickname: '管理员', is_superuser: true, is_demo: false, permissions: [] } }) })
  afterEach(() => vi.restoreAllMocks())

  it('renders operational user fields without leaking WeChat OpenID', async () => {
    vi.spyOn(userApi, 'listUsers').mockResolvedValue({
      data: { items: [{ id: 'user-1', username: 'traveler', nickname: '小游同学', avatar_url: '', is_demo: true, is_active: true, active_card_count: 2, wechat_openid: 'openid-must-not-render' }] } as never,
      meta: { page: 1, page_size: 20, total: 1 }, requestId: 'req-users',
    })
    const wrapper = mount(UsersView); await flushPromises()
    expect(wrapper.text()).toContain('小游同学')
    expect(wrapper.text()).toContain('2 张')
    expect(wrapper.text()).toContain('演示用户')
    expect(wrapper.text()).not.toContain('openid-must-not-render')
  })

  it('marks forced unbind as a confirmed non-retryable write', async () => {
    const post = vi.spyOn(http, 'apiPost').mockResolvedValue({ data: {} as never, requestId: 'req-unbind' })
    await forceUnbind('binding-1', { confirm: true, reason: '用户报告卡片遗失' })
    expect(post).toHaveBeenCalledWith('/api/v1/management/bindings/binding-1/force-unbind', { confirm: true, reason: '用户报告卡片遗失' }, false)
  })
})
