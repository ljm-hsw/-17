<script setup lang="ts">
import { FullScreen, Menu } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../../stores/auth'
import { useDisplayStore } from '../../stores/display'
import { useSceneStore } from '../../stores/scene'

const emit = defineEmits<{ 'toggle-navigation': [] }>()
const router = useRouter()
const auth = useAuthStore()
const display = useDisplayStore()
const sceneStore = useSceneStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="app-header">
    <button class="menu-button" type="button" aria-label="打开导航" @click="emit('toggle-navigation')">
      <Menu aria-hidden="true" />
    </button>

    <label class="scene-picker">
      <span class="scene-dot" aria-hidden="true" />
      <span class="sr-only">当前场景</span>
      <select
        :value="sceneStore.currentSceneId"
        :disabled="sceneStore.loading || sceneStore.scenes.length === 0"
        @change="sceneStore.selectScene(($event.target as HTMLSelectElement).value)"
      >
        <option v-for="scene in sceneStore.scenes" :key="scene.id" :value="scene.id">
          {{ scene.name }}
        </option>
      </select>
    </label>

    <div class="header-actions">
      <button class="demo-mode" type="button" @click="display.toggleDemoMode">
        <FullScreen aria-hidden="true" />
        {{ display.isDemoMode ? '退出演示' : '比赛演示' }}
      </button>
      <span class="environment">测试环境</span>
      <span class="avatar" aria-hidden="true">{{ auth.user?.nickname?.slice(0, 1) || '管' }}</span>
      <span class="username">{{ auth.user?.nickname || auth.user?.username }}</span>
      <button class="logout" type="button" @click="logout">退出</button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  min-height: 66px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 24px;
  border-bottom: 1px solid var(--tw-color-border);
  background: rgb(255 255 255 / 88%);
  backdrop-filter: blur(12px);
}

.menu-button {
  display: none;
  width: 40px;
  height: 44px;
  place-items: center;
  border: 1px solid var(--tw-color-border);
  border-radius: var(--tw-radius-sm);
  background: #fff;
  color: var(--tw-color-primary-dark);
}

.menu-button svg {
  width: 20px;
}

.scene-picker {
  display: flex;
  align-items: center;
  gap: 9px;
}

.scene-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3d9b77;
  box-shadow: 0 0 0 4px var(--tw-color-primary-soft);
}

select {
  min-height: 38px;
  border: 0;
  background: transparent;
  color: var(--tw-color-text);
  font: inherit;
  font-weight: 700;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-left: auto;
  color: var(--tw-color-muted);
  font-size: 13px;
}

.demo-mode {
  min-height: 40px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 11px;
  border: 1px solid var(--tw-color-border);
  border-radius: var(--tw-radius-sm);
  background: #fff;
  color: var(--tw-color-primary);
  font-size: 12px;
  font-weight: 700;
}

.demo-mode svg {
  width: 14px;
}

.environment {
  margin-right: 8px;
  padding: 5px 9px;
  border-radius: 999px;
  background: #fff2e6;
  color: #9b572f;
  font-size: 11px;
  font-weight: 700;
}

.avatar {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0dcc4;
  color: #72482c;
  font-weight: 800;
}

.logout {
  min-height: 40px;
  padding: 0 10px;
  border: 0;
  background: transparent;
  color: var(--tw-color-primary);
  font-weight: 700;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 767px) {
  .app-header {
    padding: 0 14px;
  }

  .menu-button {
    display: grid;
  }

  .scene-picker {
    min-width: 0;
    flex: 1;
  }

  .scene-picker select {
    min-width: 0;
    width: 100%;
    max-width: none;
  }

  .environment,
  .username,
  .demo-mode,
  .avatar {
    display: none;
  }

  .header-actions {
    flex: 0 0 auto;
  }

  .logout {
    padding: 0 4px;
    white-space: nowrap;
  }
}
</style>
