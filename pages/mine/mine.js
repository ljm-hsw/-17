const app = getApp()
Page({
  data: {
    user: { avatar: '', nickname: '凉生', identity: '浪漫探路者', aiLevel: 1 },
    stats: [
      { label: '打卡', value: 12 },
      { label: '里程', value: '5.2km' },
      { label: '游记', value: 5 },
      { label: 'AI纪念品', value: 3 }
    ],
    menus: [
      { key: 'checklist', title: '打卡清单', url: '/pages/checklist' },
      { key: 'trips', title: '旅行游记', url: '/pages/trips' },
      { key: 'ai-diary', title: 'AI游记', url: '/pages/ai-diary' },
      { key: 'my-social', title: '我的社交', url: '/pages/my-social' },
      { key: 'about', title: '关于我们', url: '/pages/about' }
    ]
  },
  onMenuTap(e) {
    const url = e.currentTarget.dataset.url
    if (url) wx.navigateTo({ url })
  },
  onSettings() { wx.navigateTo({ url: '/pages/about' }) }
})
