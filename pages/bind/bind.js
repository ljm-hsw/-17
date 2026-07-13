var app = getApp()
Page({
  data: {
    bound: false,
    bindInfo: { rfidUid: "", cardUid: "****8A3F", bindTime: "", lastSync: "刚刚", todayCount: 0 },
    inputUid: "", nfcScanning: false, nfcStatus: "点击上方按钮开始NFC读取", nfcAdapter: null
  },
  onLoad: function() {
    var bindUid = app.globalData.bindUid || wx.getStorageSync("bindUid")
    if (bindUid) {
      this.setData({ bound: true, "bindInfo.rfidUid": bindUid, "bindInfo.bindTime": wx.getStorageSync("bindTime") || "未知" })
      this.fetchTodayCount()
    }
  },
  onUnload: function() { this.stopNFC() },
  onInputUid: function(e) { this.setData({ inputUid: e.detail.value }) },
  onBindByInput: function() {
    var uid = this.data.inputUid.trim()
    if (!uid) { wx.showToast({ title: "请输入手环UID", icon: "none" }); return }
    this.doBind(uid)
  },
  onStartNFC: function() {
    if (this.data.nfcScanning) return
    if (!wx.getNFCAdapter) { wx.showToast({ title: "当前设备不支持NFC", icon: "none" }); return }
    this.setData({ nfcScanning: true, nfcStatus: "正在搜索NFC标签..." })
    var that = this
    var nfcAdapter = wx.getNFCAdapter()
    this.setData({ nfcAdapter: nfcAdapter })
    nfcAdapter.onDiscovered(function(res) {
      console.log("NFC discovered:", res)
      var uid = ""
      if (res.id) uid = that.arrayBufferToHex(res.id)
      if (uid) {
        that.setData({ nfcStatus: "已读取到手环: " + uid })
        that.stopNFC()
        that.doBind(uid)
      }
    })
    nfcAdapter.startDiscovery({
      success: function() { that.setData({ nfcStatus: "请将手环贴近手机背面..." }) },
      fail: function(err) {
        that.setData({ nfcScanning: false, nfcStatus: "NFC启动失败: " + (err.errMsg || "未知错误") })
        wx.showToast({ title: "NFC启动失败，请检查NFC开关", icon: "none" })
      }
    })
  },
  onStopNFC: function() { this.stopNFC(); this.setData({ nfcStatus: "已停止读取" }) },
  stopNFC: function() {
    if (this.data.nfcAdapter) {
      this.data.nfcAdapter.stopDiscovery({ success: function(){}, fail: function(){} })
      this.data.nfcAdapter.offDiscovered()
    }
    this.setData({ nfcScanning: false, nfcAdapter: null })
  },
  arrayBufferToHex: function(buffer) {
    if (!buffer) return ""
    var uint8 = new Uint8Array(buffer)
    var hex = ""
    for (var i = 0; i < uint8.length; i++) {
      var b = uint8[i].toString(16)
      hex += (b.length < 2 ? "0" : "") + b.toUpperCase()
    }
    return hex
  },
  doBind: function(uid) {
    wx.showLoading({ title: "绑定中..." })
    var that = this
    wx.request({
      url: app.globalData.serverUrl + "/api/bind", method: "POST",
      data: { user_id: "test_user_01", rfid_uid: uid },
      success: function(res) {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data.status === "success") {
          app.globalData.bindUid = uid
          wx.setStorageSync("bindUid", uid)
          wx.setStorageSync("bindTime", that.formatTime(new Date()))
          that.setData({ bound: true, "bindInfo.rfidUid": uid, "bindInfo.bindTime": that.formatTime(new Date()) })
          wx.showToast({ title: "绑定成功！", icon: "success" })
        } else {
          wx.showToast({ title: res.data.message || "绑定失败", icon: "error" })
        }
      },
      fail: function(err) {
        wx.hideLoading()
        wx.showToast({ title: "网络请求失败", icon: "none" })
        console.error(err)
      }
    })
  },
  onUnbind: function() {
    var that = this
    wx.showModal({
      title: "确认解绑", content: "解除绑定后将无法自动记录打卡，确定要解绑吗？",
      success: function(res) {
        if (res.confirm) {
          app.globalData.bindUid = ""
          wx.removeStorageSync("bindUid")
          wx.removeStorageSync("bindTime")
          that.setData({ bound: false, inputUid: "", nfcStatus: "点击上方按钮开始NFC读取" })
          wx.showToast({ title: "已解绑", icon: "success" })
        }
      }
    })
  },
  fetchTodayCount: function() {
    var uid = app.globalData.bindUid || wx.getStorageSync("bindUid")
    if (!uid) return
    var that = this
    wx.request({
      url: app.globalData.serverUrl + "/api/get_route/" + uid, method: "GET",
      success: function(res) {
        if (res.data.status === "success") {
          that.setData({ "bindInfo.todayCount": res.data.data ? res.data.data.length : 0 })
        }
      }
    })
  },
  formatTime: function(date) {
    var y = date.getFullYear()
    var m = (date.getMonth() + 1).toString()
    if (m.length < 2) m = "0" + m
    var d = date.getDate().toString()
    if (d.length < 2) d = "0" + d
    var h = date.getHours().toString()
    if (h.length < 2) h = "0" + h
    var min = date.getMinutes().toString()
    if (min.length < 2) min = "0" + min
    return y + "-" + m + "-" + d + " " + h + ":" + min
  }
})