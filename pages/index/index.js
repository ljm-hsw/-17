var app = getApp()
Page({
  data: {
    checkedCount: 0, totalCount: 8, progressPercent: 0,
    recommendSpots: [
      { id: 1, name: "明远湖", tag: "湖畔景观", image: "/assets/spots/mingyuan-lake.jpg" },
      { id: 2, name: "江安图书馆", tag: "学习空间", image: "/assets/spots/library.jpg" },
      { id: 3, name: "长桥", tag: "校园地标", image: "/assets/spots/long-bridge.jpg" },
      { id: 4, name: "知识广场", tag: "建筑纪念地", image: "/assets/spots/knowledge-square.jpg" }
    ]
  },
  onLoad() { this.loadCheckinProgress() },
  onShow() { this.loadCheckinProgress() },
  loadCheckinProgress() {
    var uid = app.globalData.bindUid || wx.getStorageSync("bindUid")
    if (!uid) return
    var that = this
    wx.request({
      url: app.globalData.serverUrl + "/api/get_route/" + uid, method: "GET",
      success: function(res) {
        if (res.data.status === "success") {
          var checked = res.data.data ? res.data.data.length : 0
          that.setData({ checkedCount: checked, totalCount: 8, progressPercent: Math.round((checked / 8) * 100) })
        }
      }
    })
  },
  onGoMap() { wx.navigateTo({ url: "/pages/map/map" }) },
  onGoBind() { wx.navigateTo({ url: "/pages/bind/bind" }) },
  onGoTimeline() { wx.navigateTo({ url: "/pages/timeline/timeline" }) },
  onGoTimeRecall() { wx.showToast({ title: "时光重拾功能即将上线", icon: "none" }) },
  onSpotTap(e) { wx.navigateTo({ url: "/pages/map/map?spotId=" + e.currentTarget.dataset.id }) }
})