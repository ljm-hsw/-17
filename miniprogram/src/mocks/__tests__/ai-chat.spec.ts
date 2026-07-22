import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  AI_GENERATION_UNAVAILABLE_MESSAGE,
  aiChatDemoData,
  buildRouteDemoReply,
  buildSpotDemoReply,
  findSpotIdInQuestion,
  inferQuestionType,
  isGenerationQuestionType,
} from '../ai-chat'
import { guideDemoData } from '../guide'
import { homeDemoData } from '../home'
import { recordsDemoData } from '../records'

const srcRoot = resolve(process.cwd(), 'src')
const readSource = (relativePath: string) =>
  readFileSync(resolve(srcRoot, relativePath), 'utf8')

describe('AI chat front-end demo scope', () => {
  it('keeps four quick questions and marks generation entries unavailable', () => {
    expect(aiChatDemoData.quickQuestions.map((item) => item.label)).toEqual([
      '介绍一下江安图书馆',
      '帮我规划校园游览路线',
      '根据我的打卡记录生成游记',
      '帮我写一段朋友圈文案',
    ])
    expect(aiChatDemoData.quickQuestions.map((item) => item.availability)).toEqual([
      'demo',
      'demo',
      'unavailable',
      'unavailable',
    ])
    expect(aiChatDemoData.welcomeMessage.content).toContain('当前智能体服务尚未正式接入')
  })

  it('builds local spot replies from every formal GuideSpot', () => {
    expect(guideDemoData.spots).toHaveLength(9)

    guideDemoData.spots.forEach((spot) => {
      expect(findSpotIdInQuestion(`介绍一下${spot.name}`, guideDemoData.spots)).toBe(spot.id)
      const reply = buildSpotDemoReply(spot)
      expect(reply).toContain(spot.name)
      expect(reply).toContain(spot.summary)
      expect(reply).toContain(spot.suggestedStayText)
    })
    expect(guideDemoData.spots.map((spot) => spot.name)).not.toContain('明远湖')
  })

  it('builds route advice from formal route and current demo records', () => {
    const baseReply = buildRouteDemoReply(
      guideDemoData.spots,
      guideDemoData.route.spotIds,
      recordsDemoData.records,
    )
    expect(baseReply.nextSpotId).toBe('bugao-mountain')
    expect(baseReply.content).toContain('不高山')
    expect(baseReply.content).toContain('前端演示路线')
    expect(baseReply.content).not.toContain('明远湖')

    const videoDemoReply = buildRouteDemoReply(
      guideDemoData.spots,
      guideDemoData.route.spotIds,
      [...recordsDemoData.records, { spotId: 'bugao-mountain' }],
    )
    expect(videoDemoReply.nextSpotId).toBe('east-gate-archway')
    expect(videoDemoReply.content).toContain('不高山')
  })

  it('blocks every generation keyword without exposing a generation route', () => {
    const generationQuestions = [
      '生成游记',
      '编织我的游记',
      '朋友圈文案',
      '小红书文案',
      '小红书标题',
      '短视频脚本',
      '总结今天的旅行',
      '生成旅行故事',
      '重新编织',
    ]

    generationQuestions.forEach((question) => {
      expect(isGenerationQuestionType(inferQuestionType(question))).toBe(true)
    })
    expect(AI_GENERATION_UNAVAILABLE_MESSAGE).toBe('智能体生成服务待接入')
    expect(aiChatDemoData.generationUnavailableReply).toContain('智能体生成服务将在后续接入')
  })

  it('registers only the AI chat page', () => {
    const pagesConfig = readSource('pages.json')

    expect(pagesConfig).toContain('"path": "pages/ai-chat/index"')
    expect(pagesConfig).not.toContain('"path": "pages/ai-generating/index"')
    expect(pagesConfig).not.toContain('"path": "pages/ai-result/index"')
  })

  it('restores message, quick-question and composer components without backend writes', () => {
    const chatPage = readSource('pages/ai-chat/index.vue')

    expect(chatPage).toContain('<ChatMessageBubble')
    expect(chatPage).toContain('<QuickQuestionList')
    expect(chatPage).toContain('<ChatComposer')
    expect(chatPage).toContain('@send="handleSend"')
    expect(chatPage).toContain("if (!normalizedQuestion)")
    expect(chatPage).toContain('showGenerationUnavailable')
    expect(chatPage).not.toContain('/pages/ai-generating/index')
    expect(chatPage).not.toContain('/pages/ai-result/index')
    expect(chatPage).not.toContain('uni.request')
    expect(chatPage).not.toContain('uni.setStorage')
    expect(chatPage).not.toContain('setStorageSync')
  })

  it('keeps the AI bottom navigation entry and active state', () => {
    const chatPage = readSource('pages/ai-chat/index.vue')

    expect(homeDemoData.navigation.map((item) => item.id)).toEqual(['home', 'ai', 'profile'])
    expect(chatPage).toContain('active-id="ai"')
    expect(chatPage).toContain("url: '/pages/index/index'")
    expect(chatPage).toContain("url: '/pages/profile/index'")
  })
})
