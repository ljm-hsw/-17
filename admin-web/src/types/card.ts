import type { CheckinEvent } from './dashboard'

export interface Card {
  id: string
  serial_no: string
  uid_masked: string
  status: string
  issued_at: string | null
  last_used_at: string | null
}

export interface CardCreatePayload {
  serial_no: string
  card_uid: string
}

export interface CardImportRow extends CardCreatePayload {}

export interface ImportPreviewRow {
  index: number
  serial_no: string
  uid_masked?: string
  reason?: string
}

export interface ImportPreview {
  valid: ImportPreviewRow[]
  duplicate: ImportPreviewRow[]
  invalid: ImportPreviewRow[]
}

export interface CardBinding {
  id: string
  user_id: string
  card_id: string
  alias: string
  is_primary: boolean
  bind_method: string
  bound_at: string
  unbound_at: string | null
  unbound_reason: string
  card?: Card
}

export interface ActivationCodeResult {
  id: string
  card_id: string
  activation_code: string
}

export type CardCheckin = CheckinEvent
