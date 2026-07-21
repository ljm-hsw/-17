const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function getBackendHealth(): Promise<'ok'> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`)
  if (!response.ok) throw new Error('backend_unavailable')
  const body = (await response.json()) as { data: { status: 'ok' } }
  return body.data.status
}
