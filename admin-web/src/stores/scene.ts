import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { listScenes } from '../services/management/content'
import type { Scene } from '../types/content'

const SCENE_KEY = 'travelweave.management.scene'

export const useSceneStore = defineStore('scene', () => {
  const scenes = ref<Scene[]>([])
  const currentSceneId = ref(sessionStorage.getItem(SCENE_KEY) ?? '')
  const loaded = ref(false)
  const loading = ref(false)
  const errorMessage = ref('')
  const currentScene = computed(
    () => scenes.value.find((scene) => scene.id === currentSceneId.value) ?? null,
  )

  async function loadScenes() {
    if (loaded.value || loading.value) return
    loading.value = true
    errorMessage.value = ''
    try {
      const response = await listScenes()
      scenes.value = response.data.items
      if (!scenes.value.some((scene) => scene.id === currentSceneId.value)) {
        selectScene(scenes.value[0]?.id ?? '')
      }
      loaded.value = true
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : '场景加载失败'
      throw error
    } finally {
      loading.value = false
    }
  }

  function selectScene(id: string) {
    currentSceneId.value = id
    if (id) sessionStorage.setItem(SCENE_KEY, id)
    else sessionStorage.removeItem(SCENE_KEY)
  }

  return {
    scenes,
    currentSceneId,
    currentScene,
    loading,
    errorMessage,
    loadScenes,
    selectScene,
  }
})
