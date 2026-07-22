import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import * as http from '../../../services/http'
import { rotateDeviceSecret } from '../../../services/management/devices'
import DeviceFormDrawer from '../DeviceFormDrawer.vue'

describe('device operations', () => {
  afterEach(() => vi.restoreAllMocks())

  it('clears an incompatible spot after the scene changes', async () => {
    const wrapper = mount(DeviceFormDrawer, {
      props: {
        modelValue: true,
        scenes: [
          { id: 'scene-1', slug: 'one', name: '场景一', subtitle: '', timezone: 'Asia/Shanghai', map_image_url: '', status: 'published' },
          { id: 'scene-2', slug: 'two', name: '场景二', subtitle: '', timezone: 'Asia/Shanghai', map_image_url: '', status: 'published' },
        ],
        spots: [
          { id: 'spot-1', scene_id: 'scene-1', slug: 'a', name: '点位一', category: 'checkin', summary: '', description: '', knowledge_content: '', map_x: '0.1', map_y: '0.1', tags: [], suggested_stay_minutes: 10, status: 'published', is_checkin_enabled: true, is_photo_spot: false, media: [] },
          { id: 'spot-2', scene_id: 'scene-2', slug: 'b', name: '点位二', category: 'checkin', summary: '', description: '', knowledge_content: '', map_x: '0.2', map_y: '0.2', tags: [], suggested_stay_minutes: 10, status: 'published', is_checkin_enabled: true, is_photo_spot: false, media: [] },
        ],
      },
    })
    await wrapper.setProps({ modelValue: false }); await wrapper.setProps({ modelValue: true }); await flushPromises()
    await wrapper.get('[data-test="device-scene"]').setValue('scene-1')
    await wrapper.get('[data-test="device-spot"]').setValue('spot-1')
    await wrapper.get('[data-test="device-scene"]').setValue('scene-2')
    expect((wrapper.get('[data-test="device-spot"]').element as HTMLSelectElement).value).toBe('')
  })

  it('marks secret rotation as a non-retryable high-risk write', async () => {
    const post = vi.spyOn(http, 'apiPost').mockResolvedValue({ data: {} as never, requestId: 'req' })
    await rotateDeviceSecret('device-1', { confirm: true, reason: '疑似泄露，立即轮换' })
    expect(post).toHaveBeenCalledWith(
      '/api/v1/management/devices/device-1/rotate-secret',
      { confirm: true, reason: '疑似泄露，立即轮换' },
      false,
    )
  })
})
