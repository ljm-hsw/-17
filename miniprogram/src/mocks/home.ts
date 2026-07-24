import type { HomePageData } from '../types/home'

export const homeDemoData = {
  brand: {
    title: '游迹织梦',
    subtitle: '四川大学江安校区智慧景观导览',
    logo: '/static/home/brand-logo.jpg',
  },
  heroImage: '/static/home/hero-campus.png',
  heroAlt: '四川大学江安校区校园风光',
  productPresentation: {
    label: '文创产品',
    editIcon: '/static/home/icon-edit.svg',
  },
  features: [
    {
      id: 'guide',
      title: '校园导览',
      description: ['查看校园景点', '与导览路线'],
      image: '/static/home/feature-guide.png',
    },
    {
      id: 'records',
      title: '打卡记录',
      description: ['查看已打卡', '校园点位'],
      image: '/static/home/feature-records.png',
    },
    {
      id: 'binding',
      title: '系统绑卡',
      description: ['绑定与查看', '文创产品'],
      image: '/static/home/feature-binding.png',
    },
    {
      id: 'recommend',
      title: '推荐点位',
      description: ['发现更多', '校园景点'],
      image: '/static/home/feature-recommend.png',
    },
    {
      id: 'materials',
      title: '旅程影像',
      description: ['查看旅途', '影像素材'],
      image: '/static/checkin/poses/pose-victory.png',
    },
  ],
  navigation: [
    {
      id: 'home',
      label: '首页',
      icon: '/static/home/nav-home.svg',
    },
    {
      id: 'ai',
      label: 'AI智能体',
      icon: '/static/home/nav-ai.svg',
    },
    {
      id: 'profile',
      label: '我的',
      icon: '/static/home/nav-profile.svg',
    },
  ],
} as const satisfies HomePageData
