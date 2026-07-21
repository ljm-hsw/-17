import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import * as contentApi from '../../services/management/content'
import { useSceneStore } from '../scene'

const scenes = [
  {
    id: 'jiang-an',
    slug: 'jiang-an-campus',
    name: '四川大学江安校区',
    subtitle: '智慧景观导览',
    timezone: 'Asia/Shanghai',
    map_image_url: '',
    status: 'published',
  },
  {
    id: 'wangjiang',
    slug: 'wangjiang-campus',
    name: '四川大学望江校区',
    subtitle: '',
    timezone: 'Asia/Shanghai',
    map_image_url: '',
    status: 'draft',
  },
]

describe('scene store', () => {
  beforeEach(() => {
    sessionStorage.clear()
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('loads scenes, selects the first by default and persists a later selection', async () => {
    vi.spyOn(contentApi, 'listScenes').mockResolvedValue({
      data: { items: scenes },
      meta: { page: 1, page_size: 20, total: 2 },
      requestId: 'req-scenes',
    })
    const store = useSceneStore()

    await store.loadScenes()
    expect(store.currentSceneId).toBe('jiang-an')
    expect(store.currentScene?.name).toBe('四川大学江安校区')

    store.selectScene('wangjiang')
    expect(store.currentSceneId).toBe('wangjiang')
    expect(sessionStorage.getItem('travelweave.management.scene')).toBe('wangjiang')
  })
})
