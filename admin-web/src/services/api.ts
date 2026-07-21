import { apiGet } from './http'

export async function getBackendHealth(): Promise<'ok'> {
  const response = await apiGet<{ status: 'ok' }>('/api/v1/health')
  return response.data.status
}
