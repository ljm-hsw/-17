// app.js
App({
  globalData: {
    serverUrl: "http://192.168.38.135:5000",
    bindUid: "",
    userInfo: null
  },
  onLaunch: function() {
    var bindUid = wx.getStorageSync("bindUid")
    if (bindUid) this.globalData.bindUid = bindUid
    var userInfo = wx.getStorageSync("userInfo")
    if (userInfo) this.globalData.userInfo = userInfo
  }
})