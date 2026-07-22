import type { AuditLog, CheckinRecord, RecordFilters, VisitRecord } from '../../types/records'
import { apiGet } from '../http'
function query(f:RecordFilters={}){const p=new URLSearchParams();const rows:[keyof RecordFilters,string][]=[['sceneId','scene_id'],['userId','user_id'],['visitId','visit_id'],['spotId','spot_id'],['deviceId','device_id'],['cardId','card_id'],['status','status'],['checkinType','checkin_type'],['dateFrom','date_from'],['dateTo','date_to'],['page','page'],['pageSize','page_size']];for(const [key,name] of rows){const value=f[key];if(value!==undefined&&value!=='')p.set(name,String(value))}const q=p.toString();return q?`?${q}`:''}
export const listVisits=(f:RecordFilters={})=>apiGet<{items:VisitRecord[]}>(`/api/v1/management/visits${query(f)}`)
export const getVisit=(id:string)=>apiGet<VisitRecord>(`/api/v1/management/visits/${id}`)
export const listCheckins=(f:RecordFilters={})=>apiGet<{items:CheckinRecord[]}>(`/api/v1/management/checkins${query(f)}`)
export const getCheckin=(id:string)=>apiGet<CheckinRecord>(`/api/v1/management/checkins/${id}`)
export const listAuditLogs=(f:Pick<RecordFilters,'page'|'pageSize'>={})=>apiGet<{items:AuditLog[]}>(`/api/v1/management/audit-logs${query(f)}`)
