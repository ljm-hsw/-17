import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as recordsApi from '../../../services/management/records'
import { useAuthStore } from '../../../stores/auth'
import AuditLogsView from '../../../views/AuditLogsView.vue'
import VisitDetailDrawer from '../VisitDetailDrawer.vue'

describe('management records', () => {
  beforeEach(() => { setActivePinia(createPinia()); useAuthStore().$patch({ user: { id: 'admin', username: 'admin', nickname: '管理员', is_superuser: true, is_demo: false, permissions: [] } }) })
  afterEach(() => vi.restoreAllMocks())

  it('loads a selected visit checkin trail with the visit filter', async () => {
    const list = vi.spyOn(recordsApi, 'listCheckins').mockResolvedValue({ data: { items: [] }, meta: { page: 1, page_size: 20, total: 0 }, requestId: 'req' })
    const wrapper = mount(VisitDetailDrawer, { props: { modelValue: false, visit: { id: 'visit-1', user_id: 'user-1', scene_id: 'scene-1', local_date: '2026-07-22', started_at: '2026-07-22T08:00:00Z', last_checkin_at: null } } })
    await wrapper.setProps({ modelValue: true }); await flushPromises()
    expect(list).toHaveBeenCalledWith(expect.objectContaining({ visitId: 'visit-1' }))
  })

  it('renders complete audit evidence without mutation controls', async () => {
    vi.spyOn(recordsApi, 'listAuditLogs').mockResolvedValue({ data: { items: [{ id: 'audit-1', actor_id: 'admin', actor_username: 'demo_admin', actor_role: 'superuser', action: 'device.rotate_secret', target_type: 'iot.device', target_id: 'device-1', before: { fingerprint: 'old' }, after: { fingerprint: 'new' }, reason: '疑似泄露', request_id: 'req-audit-1', created_at: '2026-07-22T10:00:00Z' }] }, meta: { page: 1, page_size: 20, total: 1 }, requestId: 'req' })
    const wrapper = mount(AuditLogsView); await flushPromises()
    const text = wrapper.text()
    expect(text).toContain('demo_admin'); expect(text).toContain('device.rotate_secret'); expect(text).toContain('疑似泄露'); expect(text).toContain('req-audit-1')
    expect(wrapper.findAll('button').map((button) => button.text())).not.toEqual(expect.arrayContaining(['新建', '编辑', '删除']))
  })
})
