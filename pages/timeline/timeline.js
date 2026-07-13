const app = getApp()

Page({
  data: {
    routeList: []
  },

  onLoad() {
    this.fetchRouteData()
  },

  fetchRouteData() {
    const uid = app.globalData.bindUid;
    if (!uid) {
      wx.showToast({ title: '未绑定卡号', icon: 'none' })
      return;
    }

    wx.showLoading({ title: '加载中...' })
    
    // 注意这里的 URL 拼接，把绑定的卡号发给后端
    wx.request({
      url: app.globalData.serverUrl + '/api/get_route/' + uid,
      method: 'GET',
      success: (res) => {
        wx.hideLoading()
        if (res.data.status === 'success') {
          this.setData({ routeList: res.data.data })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '网络失败', icon: 'none' })
      }
    })
  }
})