const app = getApp()
Page({
  data: { avatarUrl: "", nickName: "", agreed: true },
  onLoad() {
    var userInfo = wx.getStorageSync("userInfo")
    if (userInfo) {
      this.setData({ avatarUrl: userInfo.avatarUrl || "", nickName: userInfo.nickName || "" })
    }
  },
  toggleAgreement() { this.setData({ agreed: !this.data.agreed }) },
  viewAgreement(e) {
    var type = e.currentTarget.dataset.type
    wx.showModal({
      title: type === "user" ? "用户协议" : "隐私政策",
      content: type === "user" ? "本小程序仅用于四川大学江安校区智慧景观导览，记录您的游览打卡信息。" : "我们仅收集必要的微信头像和昵称信息，用于个性化展示您的游览记录。",
      showCancel: false
    })
  },
  onBindWechat() {
    if (!this.data.agreed) { wx.showToast({ title: "请先同意用户协议", icon: "none" }); return }
    var that = this
    wx.getUserProfile({
      desc: "用于展示您的游览记录",
      success: function(res) {
        var userInfo = res.userInfo
        wx.setStorageSync("userInfo", userInfo)
        app.globalData.userInfo = userInfo
        that.setData({ avatarUrl: userInfo.avatarUrl, nickName: userInfo.nickName })
        wx.showToast({ title: "绑定成功", icon: "success" })
        setTimeout(function() { wx.switchTab({ url: "/pages/index/index" }) }, 1000)
      },
      fail: function() { wx.showToast({ title: "授权已取消", icon: "none" }) }
    })
  },
  onSkip() { wx.switchTab({ url: "/pages/index/index" }) }
})