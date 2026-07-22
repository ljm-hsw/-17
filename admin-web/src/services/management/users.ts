import type { CardBinding } from '../../types/card'
import type { CheckinEvent } from '../../types/dashboard'
import type { ManagementVisitor, VisitSession } from '../../types/user'
import { apiGet, apiPost } from '../http'

export interface UserFilters { search?: string; isActive?: string; isDemo?: string; page?: number; pageSize?: number }
function query(filters: UserFilters) { const p=new URLSearchParams(); if(filters.search)p.set('search',filters.search); if(filters.isActive)p.set('is_active',filters.isActive); if(filters.isDemo)p.set('is_demo',filters.isDemo); if(filters.page)p.set('page',String(filters.page)); if(filters.pageSize)p.set('page_size',String(filters.pageSize)); const q=p.toString(); return q?`?${q}`:'' }
export const listUsers=(filters:UserFilters={})=>apiGet<{items:ManagementVisitor[]}>(`/api/v1/management/users${query(filters)}`)
export const getUser=(id:string)=>apiGet<ManagementVisitor>(`/api/v1/management/users/${id}`)
export const listUserCards=(id:string)=>apiGet<{items:CardBinding[]}>(`/api/v1/management/users/${id}/cards?page_size=100`)
export const listUserVisits=(id:string)=>apiGet<{items:VisitSession[]}>(`/api/v1/management/users/${id}/visits?page_size=20`)
export const listUserCheckins=(id:string)=>apiGet<{items:CheckinEvent[]}>(`/api/v1/management/users/${id}/checkins?page_size=20`)
export const forceUnbind=(id:string,payload:{confirm:true;reason:string})=>apiPost<typeof payload,CardBinding>(`/api/v1/management/bindings/${id}/force-unbind`,payload,false)
