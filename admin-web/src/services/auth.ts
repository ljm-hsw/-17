import type { LoginResult, ManagementUser } from '../types/auth'
import { apiGet, apiPost } from './http'

export function login(username: string, password: string) {
  return apiPost<{ username: string; password: string }, LoginResult>(
    '/api/v1/management/auth/login',
    { username, password },
    false,
  )
}

export function getManagementMe() {
  return apiGet<ManagementUser>('/api/v1/management/auth/me')
}
