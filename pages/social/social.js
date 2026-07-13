const app = getApp()
Page({
  data: {
    posts: [
      {
        id: 1,
        nickname: 'Wink',
        avatar: '/assets/avatar-default.png',
        date: '12小雨',
        title: 'day12‖终于看见日思夜想的——蓉城·成都 🐼',
        cover: '/assets/avatar-default.png',
        likes: 18,
        comments: 12,
        shares: 12
      }
    ]
  },
  onPublish() { wx.navigateTo({ url: '/pages/publish' }) },
  onPostTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/post-detail?id=' + id })
  }
})
