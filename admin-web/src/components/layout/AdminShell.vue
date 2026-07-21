<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElDrawer } from 'element-plus'

import { useSceneStore } from '../../stores/scene'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'

const mobileNavigationOpen = ref(false)
const sceneStore = useSceneStore()

onMounted(() => {
  sceneStore.loadScenes().catch(() => undefined)
})
</script>

<template>
  <div class="admin-shell">
    <div class="desktop-navigation"><AppSidebar /></div>
    <ElDrawer
      v-model="mobileNavigationOpen"
      class="mobile-navigation"
      direction="ltr"
      size="280px"
      :with-header="false"
    >
      <AppSidebar />
    </ElDrawer>
    <div class="workspace">
      <AppHeader @toggle-navigation="mobileNavigationOpen = true" />
      <main class="workspace-content"><RouterView /></main>
    </div>
  </div>
</template>

<style scoped>
.admin-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: var(--tw-sidebar-width) minmax(0, 1fr);
}

.desktop-navigation {
  position: sticky;
  top: 0;
  height: 100vh;
}

.workspace {
  min-width: 0;
}

.workspace-content {
  min-height: calc(100vh - 66px);
}

:deep(.mobile-navigation .el-drawer__body) {
  padding: 0;
}

@media (max-width: 767px) {
  .admin-shell {
    grid-template-columns: 1fr;
  }

  .desktop-navigation {
    display: none;
  }
}
</style>
