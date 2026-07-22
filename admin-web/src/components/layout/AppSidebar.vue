<script setup lang="ts">
import {
  Aim,
  Cpu,
  CreditCard,
  DataBoard,
  Document,
  Guide,
  Location,
  MapLocation,
  PictureFilled,
  Tickets,
  User,
} from '@element-plus/icons-vue'
import { computed, type Component } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../../stores/auth'
import { useDisplayStore } from '../../stores/display'

interface NavigationItem {
  label: string
  routeName?: string
  permission?: string
  icon: Component
  disabled?: boolean
  badge?: string
}

interface NavigationGroup {
  label: string
  items: NavigationItem[]
}

const router = useRouter()
const auth = useAuthStore()
const display = useDisplayStore()

const groups: NavigationGroup[] = [
  {
    label: '演示总览',
    items: [{ label: '展示看板', routeName: 'dashboard', icon: DataBoard }],
  },
  {
    label: '内容运营',
    items: [
      { label: '场景与地图', routeName: 'scenes', permission: 'scenes.view_scene', icon: MapLocation },
      { label: '点位管理', routeName: 'spots', permission: 'scenes.view_spot', icon: Location },
      { label: '游览路线', routeName: 'routes', permission: 'scenes.view_route', icon: Guide },
    ],
  },
  {
    label: '物联运营',
    items: [
      { label: '设备管理', routeName: 'devices', permission: 'iot.view_device', icon: Cpu },
      { label: '卡片与激活码', routeName: 'cards', permission: 'accounts.view_card', icon: CreditCard },
    ],
  },
  {
    label: '数据查询',
    items: [
      { label: '用户与绑定', routeName: 'users', permission: 'accounts.view_cardbinding', icon: User },
      { label: '游览记录', routeName: 'visits', permission: 'visits.view_visitsession', icon: Tickets },
      { label: '打卡事件', routeName: 'checkins', permission: 'visits.view_checkinevent', icon: Aim },
    ],
  },
  {
    label: '系统',
    items: [
      { label: '操作审计', routeName: 'audit-logs', icon: Document },
      { label: '照片与 AI', icon: PictureFilled, disabled: true, badge: '规划中' },
    ],
  },
]

const visibleGroups = computed(() =>
  groups
    .filter((group) => !display.isDemoMode || group.label === '演示总览')
    .map((group) => ({
      ...group,
      items: group.items.filter((item) => {
        if (item.disabled) return true
        if (!item.routeName || !router.hasRoute(item.routeName)) return false
        return auth.can(item.permission)
      }),
    }))
    .filter((group) => group.items.length > 0),
)
</script>

<template>
  <aside class="app-sidebar">
    <RouterLink class="brand" to="/dashboard" aria-label="游迹织梦管理中心首页">
      <span class="brand-mark" aria-hidden="true">游</span>
      <span><strong>游迹织梦</strong><small>管理中心</small></span>
    </RouterLink>

    <nav aria-label="后台主要导航">
      <section v-for="group in visibleGroups" :key="group.label" class="nav-group">
        <h2>{{ group.label }}</h2>
        <template v-for="item in group.items" :key="item.label">
          <span v-if="item.disabled" class="nav-item nav-item--disabled" aria-disabled="true">
            <component :is="item.icon" aria-hidden="true" />
            {{ item.label }}
            <small>{{ item.badge }}</small>
          </span>
          <RouterLink v-else class="nav-item" :to="{ name: item.routeName }">
            <component :is="item.icon" aria-hidden="true" />
            {{ item.label }}
          </RouterLink>
        </template>
      </section>
    </nav>

    <div class="sidebar-footer">
      <span class="online-dot" aria-hidden="true" />
      <span>测试环境<br /><small>后端管理 API</small></span>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px 14px;
  background: var(--tw-color-primary-dark);
  color: #d9e8e2;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 4px 8px 22px;
  color: #fff8ea;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border: 1px solid rgb(255 255 255 / 28%);
  border-radius: 12px;
  background: var(--tw-color-primary);
  font-family: serif;
  font-size: 19px;
  font-weight: 800;
}

.brand span:last-child {
  display: grid;
  gap: 2px;
}

.brand small,
.sidebar-footer small {
  color: #94b0a5;
  font-size: 10px;
  font-weight: 500;
}

.nav-group {
  margin-top: 10px;
}

.nav-group h2 {
  margin: 0 10px 5px;
  color: #82a397;
  font-size: 10px;
  letter-spacing: 0.12em;
}

.nav-item {
  min-height: 44px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 2px 0;
  padding: 0 11px;
  border-radius: 9px;
  color: #d4e5de;
  font-size: 13px;
  text-decoration: none;
}

.nav-item svg {
  width: 17px;
  height: 17px;
}

.nav-item:hover,
.nav-item.router-link-active {
  background: var(--tw-color-primary);
  color: #fff;
}

.nav-item--disabled {
  color: #78978c;
  cursor: not-allowed;
}

.nav-item--disabled small {
  margin-left: auto;
  padding: 2px 6px;
  border-radius: 8px;
  background: rgb(255 255 255 / 7%);
  font-size: 9px;
}

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: auto;
  padding: 16px 10px 0;
  border-top: 1px solid rgb(255 255 255 / 8%);
  font-size: 11px;
  line-height: 1.5;
}

.online-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #59c69d;
  box-shadow: 0 0 0 4px rgb(89 198 157 / 12%);
}
</style>
