export interface PageMeta {
  page: number
  page_size: number
  total: number
}

export interface ApiEnvelope<T> {
  data: T
  meta?: PageMeta
  request_id: string
}

export interface ApiFailure {
  error: {
    code: string
    message: string
    details: Record<string, string | string[]>
  }
  request_id: string
}

export interface ApiResult<T> {
  data: T
  meta?: PageMeta
  requestId: string
}

export class ApiClientError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
    public details: Record<string, string | string[]> = {},
    public requestId = '',
  ) {
    super(message)
    this.name = 'ApiClientError'
  }
}
