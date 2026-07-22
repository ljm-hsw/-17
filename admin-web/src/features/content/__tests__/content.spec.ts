import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import * as contentApi from '../../../services/management/content'
import { useAuthStore } from '../../../stores/auth'
import { useSceneStore } from '../../../stores/scene'
import type { Spot } from '../../../types/content'
import SpotFormDrawer from '../SpotFormDrawer.vue'
import SpotsView from '../../../views/SpotsView.vue'

const spot: Spot = {
  id: 'spot-1',
  scene_id: 'scene-1',
  slug: 'library',
  name: '江安图书馆',
  category: 'study',
  summary: '学习空间',
  description: '点位介绍',
  knowledge_content: '知识内容',
  map_x: '0.25',
  map_y: '0.40',
  tags: ['学习'],
  suggested_stay_minutes: 40,
  status: 'published',
  is_checkin_enabled: true,
  is_photo_spot: false,
  media: [],
}

describe('content operations', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    setActivePinia(createPinia())
    const auth = useAuthStore()
    auth.$patch({
      user: {
        id: 'admin-1', username: 'admin', nickname: '管理员',
        is_superuser: true, is_demo: false, permissions: [],
      },
    })
    const scenes = useSceneStore()
    scenes.$patch({
      currentSceneId: 'scene-1',
      scenes: [{
        id: 'scene-1', slug: 'jiang-an', name: '江安校区', subtitle: '',
        timezone: 'Asia/Shanghai', map_image_url: '', status: 'published',
      }],
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    document.body.innerHTML = ''
  })

  it('emits the complete backend spot payload with string coordinates', async () => {
    const wrapper = mount(SpotFormDrawer, {
      props: { modelValue: true, sceneId: 'scene-1', spot },
    })
    await wrapper.setProps({ modelValue: false })
    await wrapper.setProps({ modelValue: true })
    await flushPromises()

    await wrapper.get('[data-test="spot-name"]').setValue('江安图书馆新馆')
    await wrapper.get('[data-test="spot-submit"]').trigger('click')

    expect(wrapper.emitted('submit')?.[0]?.[0]).toEqual({
      scene_id: 'scene-1', slug: 'library', name: '江安图书馆新馆', category: 'study',
      summary: '学习空间', description: '点位介绍', knowledge_content: '知识内容',
      map_x: '0.25', map_y: '0.40', tags: ['学习'], suggested_stay_minutes: 40,
      is_checkin_enabled: true, is_photo_spot: false, status: 'published',
    })
  })

  it('requires a confirmed reason before disabling a spot', async () => {
    vi.spyOn(contentApi, 'listSpots').mockResolvedValue({
      data: { items: [spot] }, meta: { page: 1, page_size: 20, total: 1 }, requestId: 'req-list',
    })
    const disable = vi.spyOn(contentApi, 'disableSpot').mockResolvedValue({
      data: { ...spot, status: 'disabled' }, requestId: 'req-disable',
    })
    const wrapper = mount(SpotsView, { attachTo: document.body })
    await flushPromises()

    await wrapper.get('[data-test="disable-spot"]').trigger('click')
    await flushPromises()
    expect(disable).not.toHaveBeenCalled()

    const reason = document.body.querySelector('[data-test="risk-reason"]') as HTMLTextAreaElement
    reason.value = '点位施工，暂停对外服务'
    reason.dispatchEvent(new Event('input', { bubbles: true }))
    const confirm = document.body.querySelector('[data-test="confirm-risk"]') as HTMLButtonElement
    confirm.click()
    await flushPromises()

    expect(disable).toHaveBeenCalledWith('spot-1', {
      confirm: true,
      reason: '点位施工，暂停对外服务',
    })
    wrapper.unmount()
  })
})
