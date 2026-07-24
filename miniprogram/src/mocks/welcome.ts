import type { WelcomePageData } from '../types/welcome'
import { withRemoteAssets } from '../config/assets'

export const welcomeDemoData = withRemoteAssets({
  heroImage: '/static/welcome/welcome-hero.jpg',
  heroAlt: '游迹织梦江安校区校园桥景',
  title: '欢迎来到游迹织梦',
  description: ['绑定微信账号后，可保存打卡记录、', '发现更懂你 AI 游忆'],
  user: {
    nickname: '小游同学',
    accountLabel: '微信账号 · 本地演示',
    avatar: '/static/welcome/mock-avatar.png',
    verifiedIcon: '/static/welcome/verified.svg',
  },
  mockDisclosure: '本页使用本地演示数据，未获取真实微信资料',
  consentCheckedIcon: '/static/welcome/consent-checked.svg',
  privacyShieldIcon: '/static/welcome/privacy-shield.svg',
  privacyNotice: '仅用于您的游览记录，不会公开个人信息',
} as const satisfies WelcomePageData)
