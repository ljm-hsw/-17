const app = getApp()

Page({
  data: {
    ecoPoints: 3,
    tasksTotal: 2,
    tasksDone: 0,
    currentTask: { title: '新起点 新故事', location: '江安', progress: 60 },
    partner: { name: '陪伴者', mood: '😊', lastRecall: '2025-02-23', commProgress: 45, intimacy: 30 },
    quote: '与我产生共鸣的路线，往往都藏着相同的答案'
  },
  onGoMap() { wx.navigateTo({ url: '/pages/map' }) },
  onGoTasks() { wx.navigateTo({ url: '/pages/tasks' }) }
})
