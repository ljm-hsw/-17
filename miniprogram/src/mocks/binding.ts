import { recordsDemoData } from './records'
import type { BindingPageData } from '../types/binding'
import { withRemoteAssets } from '../config/assets'

const latestRecord = [...recordsDemoData.records].sort(
  (left, right) => Date.parse(right.checkedAt) - Date.parse(left.checkedAt),
)[0]

const maskedUid = recordsDemoData.records.find((record) => record.maskedCardUid)?.maskedCardUid

// 本页所有产品、绑定、时间与同步信息均为前端演示数据，不代表真实硬件或服务端状态。
export const bindingDemoData = withRemoteAssets({
  initialStatus: recordsDemoData.product.bindingStatus,
  defaultMethod: 'manual',
  productImage: '/static/binding/nfc-product.png',
  productImageAlt: '四川大学江安校区文创产品',
  purposes: [
    '当前页面仅演示文创产品信息绑定流程',
    '可将打卡记录关联到当前账号',
    '当前页面仅提供前端演示交互',
  ],
  bindingNotes: [
    '卡片UID仅用于本地格式校验，不会提交到服务器。',
    'NFC读取需后续结合真机能力和后端接口接入。',
  ],
  product: {
    productCode: recordsDemoData.product.productCode,
    productName: '四川大学江安校区文创产品',
    productType: '文创产品',
    alias: '我的江安冰箱贴',
    maskedUid: maskedUid ?? '••••----',
    boundAtLabel: '2025-06-11 06:20',
    lastUsedLabel: latestRecord ? `${latestRecord.checkedAtLabel}（演示）` : undefined,
    lastSyncLabel: recordsDemoData.product.lastSyncLabel,
    isPrimary: true,
    isDemo: true,
  },
} as const satisfies BindingPageData)
