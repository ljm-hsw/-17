var app = getApp()
Page({
  data: {
    activeTag: "all",
    tags: [
      { key: "all", label: "全部景点" },
      { key: "building", label: "建筑纪念地" },
      { key: "sport", label: "运动场地" },
      { key: "study", label: "学习空间" },
      { key: "park", label: "公园绿地" }
    ],
    allSpots: [
      { id: 1, name: "江安图书馆", category: "study", x: 200, y: 180, checked: false,
        tags: ["学习空间", "校园地标"], duration: "40~60分钟", bestTime: "全天", distance: "约120米",
        images: ["/assets/spots/library.jpg"],
        description: "江安图书馆是四川大学江安校区的标志性建筑，馆藏丰富，环境优雅，是同学们学习充电的首选之地。",
        history: "四川大学图书馆创建于1905年，是中国西南地区最早的现代图书馆之一。江安图书馆于2005年投入使用，建筑面积达5万余平方米，馆藏纸质文献超过700万册。" },
      { id: 2, name: "明远湖", category: "park", x: 350, y: 300, checked: false,
        tags: ["湖畔景观", "骑行推荐", "校园地标"], duration: "30~40分钟", bestTime: "日出、傍晚", distance: "约200米",
        images: ["/assets/spots/mingyuan-lake.jpg"],
        description: "明远湖是江安校区最大的人工湖，湖水清澈，四周绿树环绕，是校园内最宜人的休闲去处。",
        history: "明远湖取名自《大学》中的明远二字，寓意追求远大理想。湖面面积约200亩，是2003年校区建设时人工开凿而成。" },
      { id: 3, name: "长桥", category: "building", x: 480, y: 250, checked: false,
        tags: ["校园地标", "拍照推荐"], duration: "15~20分钟", bestTime: "日落", distance: "约350米",
        images: ["/assets/spots/long-bridge.jpg"],
        description: "长桥横跨明远湖，是连接教学区与生活区的重要通道，也是校园最具代表性的景观之一。",
        history: "长桥始建于2003年，全长约200米，是江安校区最具辨识度的建筑之一。桥身采用仿古设计，与周围自然景观和谐相融。" },
      { id: 4, name: "知识广场", category: "building", x: 150, y: 420, checked: false,
        tags: ["建筑纪念地", "活动场所"], duration: "20~30分钟", bestTime: "全天", distance: "约280米",
        images: ["/assets/spots/knowledge-square.jpg"],
        description: "知识广场位于校区中心，是举办各类校园活动的重要场所，周围环绕着多栋教学楼。",
        history: "知识广场是江安校区的中心广场，建校初期即规划为校园文化活动的核心区域。广场中央矗立着海纳百川有容乃大的校训石碑。" },
      { id: 5, name: "体育中心", category: "sport", x: 550, y: 450, checked: false,
        tags: ["运动场地"], duration: "60~90分钟", bestTime: "下午、傍晚", distance: "约500米",
        images: ["/assets/spots/sports-center.jpg"],
        description: "体育中心拥有标准田径场、游泳馆、篮球馆等多种运动设施，是师生锻炼身体的好去处。",
        history: "体育中心于2005年建成，曾承办多项省级大学生运动会赛事。田径场为标准400米跑道，可容纳观众1万余人。" },
      { id: 6, name: "东园", category: "park", x: 100, y: 300, checked: false,
        tags: ["公园绿地", "散步推荐"], duration: "20~30分钟", bestTime: "清晨、傍晚", distance: "约150米",
        images: ["/assets/spots/east-garden.jpg"],
        description: "东园是校区内的一片生态绿地，花草繁茂，鸟语花香，是晨读和散步的理想场所。",
        history: "东园原为校区东部的一片自然林地，在校园建设中被保留并改造为生态公园，种植了大量川西特色植物。" }
    ],
    spots: [],
    routeChecked: 3, routeTotal: 8,
    showPopup: false, selectedSpot: null
  },
  onLoad: function(options) {
    this.filterSpots()
    if (options.spotId) {
      var id = parseInt(options.spotId)
      var spot = null
      for (var i = 0; i < this.data.allSpots.length; i++) {
        if (this.data.allSpots[i].id === id) { spot = this.data.allSpots[i]; break }
      }
      if (spot) this.setData({ selectedSpot: spot, showPopup: true })
    }
  },
  filterSpots: function() {
    var tag = this.data.activeTag
    var filtered = tag === "all" ? this.data.allSpots : this.data.allSpots.filter(function(s) { return s.category === tag })
    this.setData({ spots: filtered })
  },
  onTagTap: function(e) {
    this.setData({ activeTag: e.currentTarget.dataset.key })
    this.filterSpots()
  },
  onSpotTap: function(e) {
    var id = parseInt(e.currentTarget.dataset.id)
    var spot = null
    for (var i = 0; i < this.data.allSpots.length; i++) {
      if (this.data.allSpots[i].id === id) { spot = this.data.allSpots[i]; break }
    }
    if (spot) this.setData({ selectedSpot: spot, showPopup: true })
  },
  closePopup: function() { this.setData({ showPopup: false }) },
  onSearchTap: function() { wx.showToast({ title: "搜索功能开发中", icon: "none" }) },
  onRoutePlan: function() { wx.showToast({ title: "路线规划功能开发中", icon: "none" }) },
  onVoiceGuide: function() { wx.showToast({ title: "语音讲解功能开发中", icon: "none" }) },
  onViewRoute: function() { wx.navigateTo({ url: "/pages/timeline/timeline" }) },
  onToggleFav: function() {
    var spot = this.data.selectedSpot
    spot.faved = !spot.faved
    this.setData({ selectedSpot: spot })
    wx.showToast({ title: spot.faved ? "已收藏" : "已取消收藏", icon: "none" })
  },
  onNavigate: function() { wx.showToast({ title: "导航功能开发中", icon: "none" }) },
  onCheckin: function() {
    var spot = this.data.selectedSpot
    spot.checked = true
    this.setData({ selectedSpot: spot })
    var allSpots = this.data.allSpots.map(function(s) { if (s.id === spot.id) s.checked = true; return s })
    this.setData({ allSpots: allSpots })
    this.filterSpots()
    wx.showToast({ title: "打卡成功！", icon: "success" })
  }
})