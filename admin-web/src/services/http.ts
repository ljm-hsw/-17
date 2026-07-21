import type { ApiEnvelope, ApiFailure, ApiResult } from '../types/api'
import { ApiClientError } from '../types/api'
import { tokenStorage } from './tokenStorage'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

let refreshPromise: Promise<string> | null = null

async function parseFailure(response: Response): Promise<ApiClientError> {
  const payload = (await response.json()) as ApiFailure
  return new ApiClientError(
    payload.error.code,
    payload.error.message,
    response.status,
    payload.error.details,
    payload.request_id,
  )
}

async function refreshAccess(): Promise<string> {
  if (refreshPromise) return refreshPromise

  refreshPromise = (async () => {
    const refresh = tokenStorage.get().refresh
    if (!refresh) throw new ApiClientError('AUTH_REQUIRED', '请重新登录', 401)

    const response = await fetch(`${apiBaseUrl}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    })
    if (!response.ok) throw await parseFailure(response)

    const payload = (await response.json()) as ApiEnvelope<{ access: string }>
    tokenStorage.saveAccess(payload.data.access)
    return payload.data.access
  })()

  try {
    return await refreshPromise
  } catch (error) {
    tokenStorage.clear()
    throw error
  } finally {
    refreshPromise = null
  }
}

async function apiRequest<T>(
  path: string,
  init: RequestInit,
  allowRetry: boolean,
  retried = false,
): Promise<ApiResult<T>> {
  const access = tokenStorage.get().access
  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  if (access) headers.set('Authorization', `Bearer ${access}`)

  let response: Response
  try {
    response = await fetch(`${apiBaseUrl}${path}`, { ...init, headers })
  } catch {
    throw new ApiClientError('NETWORK_ERROR', '网络连接失败，请稍后重试', 0)
  }

  if (response.status === 401 && allowRetry && !retried && tokenStorage.get().refresh) {
    const renewedAccess = await refreshAccess()
    headers.set('Authorization', `Bearer ${renewedAccess}`)
    return apiRequest<T>(path, { ...init, headers }, allowRetry, true)
  }
  if (!response.ok) throw await parseFailure(response)

  const payload = (await response.json()) as ApiEnvelope<T>
  return {
    data: payload.data,
    meta: payload.meta,
    requestId: payload.request_id,
  }
}

export function apiGet<T>(path: string): Promise<ApiResult<T>> {
  return apiRequest<T>(path, { method: 'GET' }, true)
}

export function apiPost<TBody, TData>(
  path: string,
  body: TBody,
  allowRetry = true,
): Promise<ApiResult<TData>> {
  return apiRequest<TData>(
    path,
    { method: 'POST', body: JSON.stringify(body) },
    allowRetry,
  )
}

export function apiPatch<TBody, TData>(
  path: string,
  body: TBody,
  allowRetry = true,
): Promise<ApiResult<TData>> {
  return apiRequest<TData>(
    path,
    { method: 'PATCH', body: JSON.stringify(body) },
    allowRetry,
  )
}
