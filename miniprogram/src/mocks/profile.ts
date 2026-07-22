import type {
  ProfilePageData,
  ProfileRecordSource,
  ProfileSpotSource,
  ProfileStats,
} from '../types/profile'
import { buildCheckinOverview } from './records'

export const profileDemoData = {
  user: {
    nickname: '校园漫游者',
    roleLabel: '江安校区探索者',
    avatar: '/static/common/user-avatar-default.png',
    demoLabel: '前端演示资料',
    isDemo: true,
  },
  serviceItems: [
    {
      id: 'feedback',
      title: '提交意见',
      iconText: '意',
    },
    {
      id: 'about-device',
      title: '关于设备',
      iconText: '设',
    },
  ],
} as const satisfies ProfilePageData

export function buildProfileStats(
  records: readonly ProfileRecordSource[],
  spots: readonly ProfileSpotSource[],
): ProfileStats {
  const overview = buildCheckinOverview(records, spots)

  return {
    checkedCount: overview.checkedCount,
    totalCount: overview.totalCount,
    uncheckedCount: overview.uncheckedCount,
    completionRate: overview.progressPercentage,
    digitalCardCount: overview.checkedCount,
  }
}
