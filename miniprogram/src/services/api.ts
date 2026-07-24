const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function getBackendHealth(): Promise<'ok'> {
  const response = await uni.request({
    url: `${apiBaseUrl}/api/v1/health`,
    method: 'GET',
  })
  if (response.statusCode !== 200) throw new Error('backend_unavailable')
  const body = response.data as { data: { status: 'ok' } }
  return body.data.status
}
