import type {
  ActivationCodeResult, Card, CardBinding, CardCheckin, CardCreatePayload,
  CardImportRow, ImportPreview,
} from '../../types/card'
import { apiGet, apiPatch, apiPost } from '../http'

export interface CardFilters { search?: string; status?: string; page?: number; pageSize?: number }
function query(filters: CardFilters) {
  const params = new URLSearchParams()
  if (filters.search) params.set('search', filters.search)
  if (filters.status) params.set('status', filters.status)
  if (filters.page) params.set('page', String(filters.page))
  if (filters.pageSize) params.set('page_size', String(filters.pageSize))
  const value = params.toString(); return value ? `?${value}` : ''
}

export const listCards = (filters: CardFilters = {}) => apiGet<{ items: Card[] }>(`/api/v1/management/cards${query(filters)}`)
export const getCard = (id: string) => apiGet<Card>(`/api/v1/management/cards/${id}`)
export const createCard = (payload: CardCreatePayload) => apiPost<CardCreatePayload, Card>('/api/v1/management/cards', payload, false)
export const updateCard = (id: string, payload: Pick<Card, 'serial_no' | 'status'>) => apiPatch<typeof payload, Card>(`/api/v1/management/cards/${id}`, payload)
export const previewCardImport = (rows: CardImportRow[]) => apiPost<{ rows: CardImportRow[] }, ImportPreview>('/api/v1/management/cards/import-preview', { rows })
export const confirmCardImport = (rows: CardImportRow[]) => apiPost<{ rows: CardImportRow[]; confirm: true }, { items: Card[] }>('/api/v1/management/cards/import-confirm', { rows, confirm: true }, false)
export const createActivationCode = (id: string) => apiPost<Record<string, never>, ActivationCodeResult>(`/api/v1/management/cards/${id}/activation-codes`, {}, false)
export const listCardBindings = (id: string) => apiGet<{ items: CardBinding[] }>(`/api/v1/management/cards/${id}/bindings?page_size=100`)
export const listCardCheckins = (id: string) => apiGet<{ items: CardCheckin[] }>(`/api/v1/management/cards/${id}/checkins?page_size=8`)
