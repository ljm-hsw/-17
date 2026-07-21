import type { Scene } from '../../types/content'
import { apiGet } from '../http'

export function listScenes() {
  return apiGet<{ items: Scene[] }>('/api/v1/management/scenes')
}
