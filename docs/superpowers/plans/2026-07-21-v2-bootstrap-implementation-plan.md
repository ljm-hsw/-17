# 游迹织梦 v2 工程框架实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `chore/bootstrap-v2` 分支上，从零建立供团队并行开发的 Django 后端、Vue Web 管理端、uni-app 微信小程序、ESP32 Arduino 设备端和统一工程规范。

**Architecture:** 单仓库包含四个正式运行端，Django + DRF 是唯一业务后端和数据库访问者；Web 管理端、小程序和设备端只能通过各自受控 API 访问后端。此次仅建立工程骨架、健康检查、质量门禁和协作规范，不实现尚未确认的业务接口。

**Tech Stack:** Python 3.12、Django 5.2 LTS、Django REST Framework、PostgreSQL、Vue 3、TypeScript、Vite、Element Plus、ECharts、uni-app Vue 3/Vite/TypeScript、ESP32 Arduino Framework、PlatformIO、GitHub Actions。

## Global Constraints

- 工作分支固定为 `chore/bootstrap-v2`；不得直接修改或推送 `master`。
- 旧原生微信小程序 MVP 不迁移到 v2 目录；它继续保留在 `master` 历史中。
- 正式代码顶层目录固定为 `backend/`、`admin-web/`、`miniprogram/`、`firmware/`、`infra/`、`docs/`。
- 后端运行时固定为 Python 3.12；Django 使用 5.2 LTS 系列。
- Node.js 固定为 24 LTS；仓库内所有 Node 项目使用 npm，并提交各自的 `package-lock.json`。
- 本地、测试和部署数据库均使用 PostgreSQL，不把 SQLite 作为 v2 正式路径。
- 所有真实密钥只来自环境变量；仓库只提交 `.env.example`。
- API 统一使用 `/api/v1/` 前缀；本计划只实现无业务数据的 `/api/v1/health`。
- `User` 自项目首次迁移起就是自定义模型，避免后续切换用户模型。
- 每个任务通过测试、检查和独立提交后才能进入下一个任务。
- 提交信息使用 Conventional Commits，例如 `chore: bootstrap repository structure`。

---

### Task 1: 清理旧 MVP 并建立团队仓库骨架

**Files:**
- Remove: `app.js`, `app.json`, `app.wxss`, `assets/`, `pages/`, `project.config.json`, `project.private.config.json`, `sitemap.json`, `utils/`
- Modify: `.gitignore`
- Create: `.editorconfig`
- Create: `.gitattributes`
- Create: `.python-version`
- Create: `.nvmrc`
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `.github/pull_request_template.md`
- Create: `.github/ISSUE_TEMPLATE/bug.yml`
- Create: `.github/ISSUE_TEMPLATE/feature.yml`
- Create: `backend/.gitkeep`
- Create: `admin-web/.gitkeep`
- Create: `miniprogram/.gitkeep`
- Create: `firmware/.gitkeep`
- Create: `infra/.gitkeep`

**Interfaces:**
- Consumes: 当前 `master` 上的旧 MVP 文件和已确认的三份设计文档。
- Produces: 统一顶层目录、工具版本约束、贡献规则和 PR/Issue 模板。

- [ ] **Step 1: 验证当前分支和旧 MVP 文件**

Run:

```bash
git branch --show-current
test -f app.js
test -d pages
```

Expected: 第一条输出 `chore/bootstrap-v2`，后两条退出码均为 0。

- [ ] **Step 2: 从 v2 分支移除旧 MVP**

Run:

```bash
git rm -r app.js app.json app.wxss assets pages project.config.json project.private.config.json sitemap.json utils
```

Expected: Git 暂存上述旧 MVP 删除；`master` 历史不受影响。

- [ ] **Step 3: 建立固定目录和工具版本文件**

Create `.python-version`:

```text
3.12
```

Create `.nvmrc`:

```text
24
```

Create `.editorconfig`:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2
trim_trailing_whitespace = true

[*.py]
indent_size = 4

[*.md]
trim_trailing_whitespace = false
```

Create `.gitattributes`:

```gitattributes
* text=auto eol=lf
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.webp binary
*.pdf binary
```

Replace `.gitignore` with:

```gitignore
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp
*.tmp

.env
.env.*
!.env.example

__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.venv/
htmlcov/
.coverage

node_modules/
dist/
coverage/
miniprogram/unpackage/
miniprogram/.hbuilderx/

.pio/
firmware/.vscode/
firmware/include/config.h
```

Run:

```bash
mkdir -p backend admin-web miniprogram firmware infra .github/ISSUE_TEMPLATE
touch backend/.gitkeep admin-web/.gitkeep miniprogram/.gitkeep firmware/.gitkeep infra/.gitkeep
```

Expected: 六个正式顶层目录均存在。

- [ ] **Step 4: 编写团队入口文档**

Create `README.md` with these exact sections and content:

```markdown
# 游迹织梦

面向文旅场景的软硬件一体化物联网感知与个性化智能服务系统。当前最终参赛版本以四川大学江安校区为首个 Scene。

## 系统组成

- `backend/`：Django + DRF 唯一业务后端
- `admin-web/`：Vue 3 展示与运营管理端
- `miniprogram/`：uni-app 微信小程序
- `firmware/`：ESP32 Arduino 设备端
- `infra/`：本地与部署基础设施
- `docs/`：产品、架构、接口和计划文档

## 开发原则

1. 不直接向 `master` 推送代码。
2. 每项改动从短生命周期分支开始，并通过 Pull Request 合入。
3. 后端是唯一可信数据源；其他端不得直接访问数据库。
4. 业务接口以 `docs/` 中已确认的契约为准。
5. 新功能和修复必须包含对应测试。

## 快速开始

各端的安装和运行命令在对应目录 README 中维护。完整协作流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。
```

Create `CONTRIBUTING.md`:

```markdown
# 团队协作规范

## 分支

- `master`：受保护的稳定分支，仅通过 Pull Request 合入。
- `feat/<scope>-<name>`：新功能。
- `fix/<scope>-<name>`：缺陷修复。
- `docs/<name>`：仅文档变更。
- `chore/<name>`：工程、依赖和工具变更。

每个分支只解决一个可独立评审的问题，不在同一 PR 混入无关重构。

## 提交

使用 Conventional Commits：`type(scope): summary`。允许的 type 为 `feat`、`fix`、`docs`、`test`、`refactor`、`chore`、`ci`。

示例：

- `feat(visits): add daily visit session model`
- `fix(iot): keep checkin event idempotent`
- `docs(api): define card binding errors`

## Pull Request

1. 从最新 `master` 创建分支。
2. 本地运行受影响端的测试、格式检查和构建。
3. 填写 PR 模板，说明范围、验证证据和接口/数据影响。
4. 至少一名非作者成员评审后合入。
5. 优先使用 squash merge，保持 `master` 历史清晰。

## 安全

禁止提交微信密钥、数据库密码、设备密钥、卡 UID 明文、激活码明文、Dify/模型密钥和真实用户数据。发现泄露时立即撤销凭据，不得只删除 Git 文件。
```

- [ ] **Step 5: 添加 PR 模板**

Create `.github/pull_request_template.md`:

```markdown
## 变更目的

<!-- 说明用户问题、技术问题或对应文档。 -->

## 变更范围

- [ ] Backend
- [ ] Admin Web
- [ ] Mini Program
- [ ] Firmware
- [ ] Infra / Docs

## 验证证据

<!-- 列出实际运行的命令和结果。 -->

## 接口与数据影响

- [ ] 无接口变化
- [ ] 已同步 OpenAPI/API 契约
- [ ] 包含数据库迁移及回滚说明

## 安全与隐私

- [ ] 未提交密钥或真实个人数据
- [ ] 敏感字段已脱敏并由后端鉴权

## Review Checklist

- [ ] 范围单一，无无关改动
- [ ] 测试、格式检查和构建通过
- [ ] 文档已同步
```

Create `.github/ISSUE_TEMPLATE/bug.yml`:

```yaml
name: Bug
description: 报告可复现的问题
title: "fix: "
labels: ["bug"]
body:
  - type: textarea
    id: description
    attributes:
      label: 问题描述
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: 复现步骤
      placeholder: "1. 打开…\n2. 点击…\n3. 观察…"
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: 期望与实际结果
    validations:
      required: true
  - type: input
    id: scope
    attributes:
      label: 受影响端或接口
      placeholder: "backend / admin-web / miniprogram / firmware"
    validations:
      required: true
  - type: input
    id: owner
    attributes:
      label: 建议负责人
```

Create `.github/ISSUE_TEMPLATE/feature.yml`:

```yaml
name: Feature
description: 提议一个可验收的功能
title: "feat: "
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: 用户问题
    validations:
      required: true
  - type: textarea
    id: scope
    attributes:
      label: 功能范围
    validations:
      required: true
  - type: textarea
    id: acceptance
    attributes:
      label: 验收标准
      placeholder: "- [ ] 给定…当…则…"
    validations:
      required: true
  - type: input
    id: api
    attributes:
      label: 受影响接口或数据模型
  - type: input
    id: owner
    attributes:
      label: 建议负责人
```

Validate both with a YAML parser in Task 7.

- [ ] **Step 6: 验证骨架**

Run:

```bash
test ! -e app.js
test -d backend
test -d admin-web
test -d miniprogram
test -d firmware
test -d infra
test -f docs/superpowers/specs/2026-07-13-jiang-an-mvp-product-business-design.md
```

Expected: 全部退出码为 0。

- [ ] **Step 7: 提交**

```bash
git add .
git commit -m "chore: establish v2 repository structure"
```

---

### Task 2: 建立 Django + DRF 后端基础

**Files:**
- Create: `backend/requirements/base.txt`
- Create: `backend/requirements/dev.txt`
- Create: `backend/manage.py`
- Create: `backend/config/settings/base.py`
- Create: `backend/config/settings/local.py`
- Create: `backend/config/settings/test.py`
- Create: `backend/config/settings/production.py`
- Create: `backend/config/urls.py`
- Create: `backend/apps/common/views.py`
- Create: `backend/apps/accounts/models.py`
- Create: `backend/tests/test_health.py`
- Create: `backend/tests/test_user_model.py`
- Create: `backend/pytest.ini`
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/README.md`

**Interfaces:**
- Consumes: Python 3.12、PostgreSQL `DATABASE_URL`、`/api/v1/` 命名规则。
- Produces: `GET /api/v1/health`、自定义 `accounts.User`、可创建 OpenAPI schema 的 DRF 项目。

- [ ] **Step 1: 创建并锁定基础依赖**

Create `backend/requirements/base.txt`:

```text
Django~=5.2.0
djangorestframework~=3.16.0
drf-spectacular~=0.28.0
django-environ~=0.12.0
psycopg[binary]~=3.2.0
```

Create `backend/requirements/dev.txt`:

```text
-r base.txt
pytest~=8.4.0
pytest-django~=4.11.0
ruff~=0.12.0
```

Run:

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements/dev.txt
.venv/bin/django-admin startproject config .
```

Expected: Django 项目创建成功，依赖安装无冲突。

- [ ] **Step 2: 先写健康检查失败测试**

Create `backend/pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
```

Create `backend/tests/test_health.py`:

```python
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_endpoint_returns_stable_envelope(client):
    response = client.get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"data": {"status": "ok"}}
```

Run:

```bash
cd backend
.venv/bin/pytest tests/test_health.py -q
```

Expected: FAIL，因为 `health` URL 尚不存在。

- [ ] **Step 3: 实现最小健康检查**

Create `backend/apps/common/views.py`:

```python
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"data": {"status": "ok"}})
```

Configure `backend/config/urls.py`:

```python
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.common.views import HealthView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health", HealthView.as_view(), name="health"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
```

Run the health test again. Expected: PASS.

- [ ] **Step 4: 先写自定义用户模型失败测试**

Create `backend/tests/test_user_model.py`:

```python
import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_custom_user_uses_uuid_primary_key():
    user = get_user_model().objects.create_user(username="owner")

    assert user._meta.label == "accounts.User"
    assert user.id.version == 4
```

Run:

```bash
cd backend
.venv/bin/pytest tests/test_user_model.py -q
```

Expected: FAIL，因为默认用户主键不是 UUID，且模型标签不是 `accounts.User`。

- [ ] **Step 5: 实现自定义用户和模块边界**

Create `backend/apps/accounts/models.py`:

```python
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wechat_openid = models.CharField(max_length=128, unique=True, null=True, blank=True)
```

Generate the seven Django apps with exact commands:

```bash
cd backend
mkdir -p apps
touch apps/__init__.py
for app in common accounts scenes iot visits media ai; do
  mkdir -p "apps/$app"
  .venv/bin/python manage.py startapp "$app" "apps/$app"
done
```

Replace the generated config classes with these exact names and dotted paths:

```python
# backend/apps/common/apps.py
from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

# backend/apps/accounts/apps.py: AccountsConfig, name = "apps.accounts"
# backend/apps/scenes/apps.py: ScenesConfig, name = "apps.scenes"
# backend/apps/iot/apps.py: IotConfig, name = "apps.iot"
# backend/apps/visits/apps.py: VisitsConfig, name = "apps.visits"
# backend/apps/media/apps.py: MediaConfig, name = "apps.media"
# backend/apps/ai/apps.py: AiConfig, name = "apps.ai"
```

Each of the six abbreviated files above has the same three-line `AppConfig` body as `CommonConfig`, using exactly the class name and dotted `name` shown. Add the following entries to `INSTALLED_APPS`:

```python
"rest_framework",
"drf_spectacular",
"apps.common",
"apps.accounts",
"apps.scenes",
"apps.iot",
"apps.visits",
"apps.media",
"apps.ai",
```

Set:

```python
AUTH_USER_MODEL = "accounts.User"
TIME_ZONE = "Asia/Shanghai"
USE_TZ = True
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
```

Split settings so `local.py`, `test.py`, and `production.py` import `base.py`; all environments read PostgreSQL from `DATABASE_URL`. Generate the initial accounts migration.

Run:

```bash
cd backend
.venv/bin/python manage.py makemigrations accounts
.venv/bin/python manage.py check
.venv/bin/pytest -q
```

Expected: migrations created, system check clean, 2 tests pass.

- [ ] **Step 6: 配置 Ruff 并验证**

Create `backend/pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.ruff.format]
quote-style = "double"
```

Run:

```bash
cd backend
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

Expected: 两项检查通过。

- [ ] **Step 7: 提交**

```bash
git add backend
git commit -m "feat(backend): scaffold django api foundation"
```

---

### Task 3: 建立 PostgreSQL 本地基础设施

**Files:**
- Create: `infra/compose.yaml`
- Create: `infra/.env.example`
- Create: `infra/README.md`
- Modify: `backend/.env.example`
- Test: `backend/tests/test_database_vendor.py`

**Interfaces:**
- Consumes: 后端 `DATABASE_URL`。
- Produces: 本地 PostgreSQL 16 服务和统一健康检查。

- [ ] **Step 1: 写 PostgreSQL 约束失败测试**

Create `backend/tests/test_database_vendor.py`:

```python
from django.db import connection


def test_v2_uses_postgresql():
    assert connection.vendor == "postgresql"
```

Run against an unset local database. Expected: FAIL 或连接错误，证明环境尚未配置。

- [ ] **Step 2: 添加 Compose 服务**

Create `infra/compose.yaml`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: travelweave
      POSTGRES_USER: travelweave
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-travelweave_dev}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U travelweave -d travelweave"]
      interval: 5s
      timeout: 5s
      retries: 10
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Create `backend/.env.example`:

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_SECRET_KEY=replace-with-local-secret
DATABASE_URL=postgresql://travelweave:travelweave_dev@localhost:5432/travelweave
ALLOWED_HOSTS=localhost,127.0.0.1
```

- [ ] **Step 3: 启动数据库并验证迁移**

Run:

```bash
docker compose --env-file infra/.env.example -f infra/compose.yaml up -d postgres
cd backend
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/pytest -q
```

Expected: PostgreSQL 健康，迁移成功，3 个测试通过。

- [ ] **Step 4: 提交**

```bash
git add infra backend/.env.example backend/tests/test_database_vendor.py
git commit -m "chore(infra): add postgresql development environment"
```

---

### Task 4: 建立 Vue Web 管理端基础

**Files:**
- Create: `admin-web/package.json`
- Create: `admin-web/src/main.ts`
- Create: `admin-web/src/router/index.ts`
- Create: `admin-web/src/services/api.ts`
- Create: `admin-web/src/views/DashboardView.vue`
- Create: `admin-web/src/App.vue`
- Create: `admin-web/src/views/__tests__/DashboardView.spec.ts`
- Create: `admin-web/.env.example`
- Create: `admin-web/README.md`

**Interfaces:**
- Consumes: `GET /api/v1/health`，环境变量 `VITE_API_BASE_URL`。
- Produces: 可测试、可构建的管理端壳层和后端状态展示。

- [ ] **Step 1: 使用官方 Vue TypeScript 模板创建项目**

Run:

```bash
npm create vite@latest admin-web -- --template vue-ts --no-interactive
cd admin-web
npm install
npm install vue-router pinia axios element-plus echarts
npm install --save-dev vitest @vue/test-utils jsdom
```

Expected: `package-lock.json` 已创建，Vite 开发构建可运行。

- [ ] **Step 2: 先写后端状态失败测试**

Create `admin-web/src/views/__tests__/DashboardView.spec.ts`:

```typescript
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import DashboardView from '../DashboardView.vue'

describe('DashboardView', () => {
  afterEach(() => vi.restoreAllMocks())

  it('shows the backend health result', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: { status: 'ok' } }),
    }))

    const wrapper = mount(DashboardView)
    await flushPromises()

    expect(wrapper.get('[data-test="backend-status"]').text()).toContain('正常')
  })
})
```

Add `"test": "vitest run"` to the generated `package.json` scripts. Create `vitest.config.ts` in Step 3, then run `npm test` before Step 3 to confirm the missing component failure.

Expected: FAIL because `DashboardView.vue` does not exist.

- [ ] **Step 3: 实现最小管理端壳层**

Create `admin-web/src/services/api.ts`:

```typescript
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function getBackendHealth(): Promise<'ok'> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`)
  if (!response.ok) throw new Error('backend_unavailable')
  const body = (await response.json()) as { data: { status: 'ok' } }
  return body.data.status
}
```

Create `admin-web/src/views/DashboardView.vue`:

```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getBackendHealth } from '../services/api'

const status = ref<'loading' | 'ok' | 'error'>('loading')

onMounted(async () => {
  try {
    status.value = await getBackendHealth()
  } catch {
    status.value = 'error'
  }
})
</script>

<template>
  <main>
    <h1>游迹织梦管理中心</h1>
    <p data-test="backend-status">
      后端状态：{{ status === 'ok' ? '正常' : status === 'error' ? '不可用' : '检查中' }}
    </p>
  </main>
</template>
```

Create `admin-web/src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from '../views/DashboardView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: DashboardView },
  ],
})
```

Replace `admin-web/src/main.ts`:

```typescript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import { router } from './router'

createApp(App).use(router).use(ElementPlus).mount('#app')
```

Replace `admin-web/src/App.vue`:

```vue
<template>
  <RouterView />
</template>
```

Create `admin-web/vitest.config.ts`:

```typescript
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [vue()],
  test: { environment: 'jsdom' },
})
```

Run:

```bash
cd admin-web
npm test
npm run build
```

Expected: test passes and production build succeeds.

- [ ] **Step 4: 添加环境和团队说明**

Create `admin-web/.env.example`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Create `admin-web/README.md`:

````markdown
# Web 管理端

运行环境：Node.js 24 LTS，依赖管理：npm。

```bash
npm ci
npm run dev
npm test
npm run build
```

复制 `.env.example` 为 `.env.local`，只在本机填写后端地址。管理端不得保存数据库、设备或模型服务密钥。
````

- [ ] **Step 5: 提交**

```bash
git add admin-web
git commit -m "feat(admin-web): scaffold vue management shell"
```

---

### Task 5: 建立 uni-app 微信小程序基础

**Files:**
- Create: `miniprogram/package.json`
- Create: `miniprogram/src/App.vue`
- Create: `miniprogram/src/main.ts`
- Create: `miniprogram/src/pages.json`
- Create: `miniprogram/src/manifest.json`
- Create: `miniprogram/src/pages/index/index.vue`
- Create: `miniprogram/src/services/api.ts`
- Create: `miniprogram/src/services/__tests__/api.spec.ts`
- Create: `miniprogram/.env.example`
- Create: `miniprogram/README.md`

**Interfaces:**
- Consumes: `GET /api/v1/health`，`VITE_API_BASE_URL`。
- Produces: 可编译至微信小程序的 Vue 3 + TypeScript 工程和统一 API Client 入口。

- [ ] **Step 1: 使用 uni-app 官方 Vue 3/Vite/TypeScript 模板**

Run:

```bash
npx degit dcloudio/uni-preset-vue#vite-ts miniprogram
cd miniprogram
npm install
npm install --save-dev vitest
```

Expected: `package-lock.json` 已创建，模板使用 `@dcloudio/vite-plugin-uni`。

- [ ] **Step 2: 先写 API Client 失败测试**

Create `miniprogram/src/services/__tests__/api.spec.ts`:

```typescript
import { afterEach, describe, expect, it, vi } from 'vitest'

import { getBackendHealth } from '../api'

describe('getBackendHealth', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('unwraps the stable API envelope', async () => {
    vi.stubGlobal('uni', {
      request: vi.fn().mockResolvedValue({
        statusCode: 200,
        data: { data: { status: 'ok' } },
      }),
    })

    await expect(getBackendHealth()).resolves.toBe('ok')
  })
})
```

Run `npm test`. Expected: FAIL because `src/services/api.ts` does not exist.

- [ ] **Step 3: 实现最小 API Client 和首页**

Create `miniprogram/src/services/api.ts`:

```typescript
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

export async function getBackendHealth(): Promise<'ok'> {
  const response = await uni.request<{ data: { status: 'ok' } }>({
    url: `${apiBaseUrl}/api/v1/health`,
    method: 'GET',
  })
  if (response.statusCode !== 200) throw new Error('backend_unavailable')
  return response.data.data.status
}
```

Replace `miniprogram/src/pages/index/index.vue`:

```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getBackendHealth } from '../../services/api'

const backendStatus = ref('检查中')

onMounted(async () => {
  try {
    backendStatus.value = (await getBackendHealth()) === 'ok' ? '正常' : '不可用'
  } catch {
    backendStatus.value = '不可用'
  }
})
</script>

<template>
  <view class="page">
    <text class="title">游迹织梦</text>
    <text class="subtitle">四川大学江安校区</text>
    <text class="status">开发环境后端：{{ backendStatus }}</text>
  </view>
</template>

<style scoped>
.page { min-height: 100vh; padding: 80rpx 40rpx; background: #f5efe6; }
.title { display: block; color: #2b4c3f; font-size: 48rpx; font-weight: 700; }
.subtitle, .status { display: block; margin-top: 20rpx; color: #5a6b63; font-size: 28rpx; }
</style>
```

Do not migrate old MVP page logic or mock visitor data. Add `"test": "vitest run"` to the generated `package.json` scripts.

Create `miniprogram/.env.example`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

- [ ] **Step 4: 验证测试与微信构建**

Run:

```bash
cd miniprogram
npm test
npm run build:mp-weixin
```

Expected: tests pass and `dist/build/mp-weixin` is generated.

- [ ] **Step 5: 提交**

```bash
git add miniprogram
git commit -m "feat(miniprogram): scaffold uni-app wechat client"
```

---

### Task 6: 建立 ESP32 Arduino 设备端基础

**Files:**
- Create: `firmware/platformio.ini`
- Create: `firmware/src/main.cpp`
- Create: `firmware/include/config.example.h`
- Create: `firmware/test/test_event_id/test_main.cpp`
- Create: `firmware/README.md`

**Interfaces:**
- Consumes: ESP32 Arduino Framework；不实现未确认的 RFID 引脚和事件 HTTP 契约。
- Produces: 可由 PlatformIO 重复编译的设备工程、配置模板和事件 ID 单元测试入口。

- [ ] **Step 1: 添加 PlatformIO 配置**

Create `firmware/platformio.ini`:

```ini
[platformio]
default_envs = esp32dev

[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
test_framework = unity
build_flags = -D CORE_DEBUG_LEVEL=0
```

- [ ] **Step 2: 先写最小失败测试**

Create `firmware/test/test_event_id/test_main.cpp`:

```cpp
#include <array>
#include <string>

#include <unity.h>

#include "event_id.h"

void test_event_id_is_32_lowercase_hex_characters() {
  const std::array<uint32_t, 4> words = {0x01234567, 0x89abcdef, 0x00000001, 0xffffffff};
  const std::string value = formatEventId(words);

  TEST_ASSERT_EQUAL_UINT32(32, value.size());
  TEST_ASSERT_EQUAL_STRING("0123456789abcdef00000001ffffffff", value.c_str());
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_event_id_is_32_lowercase_hex_characters);
  return UNITY_END();
}
```

Append the native test environment to `firmware/platformio.ini`:

```ini
[env:native]
platform = native
test_framework = unity
build_src_filter = +<event_id.cpp> -<main.cpp>
```

Run:

```bash
cd firmware
pio test -e native
```

Expected: FAIL because `formatEventId()` does not exist.

- [ ] **Step 3: 实现可测试的设备启动骨架**

Create `firmware/include/event_id.h`:

```cpp
#pragma once

#include <array>
#include <cstdint>
#include <string>

#ifdef ARDUINO
#include <Arduino.h>
String makeEventId();
#endif

std::string formatEventId(const std::array<uint32_t, 4>& words);
```

Create `firmware/src/event_id.cpp`:

```cpp
#include <cstdio>

#include "event_id.h"

#ifdef ARDUINO
#include <esp_system.h>
#endif

std::string formatEventId(const std::array<uint32_t, 4>& words) {
  char value[33];
  for (int index = 0; index < 4; ++index) {
    std::snprintf(value + index * 8, 9, "%08lx", static_cast<unsigned long>(words[index]));
  }
  value[32] = '\0';
  return std::string(value);
}

#ifdef ARDUINO
String makeEventId() {
  const std::array<uint32_t, 4> words = {esp_random(), esp_random(), esp_random(), esp_random()};
  return String(formatEventId(words).c_str());
}
#endif
```

Create `firmware/src/main.cpp`:

```cpp
#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial.println("travelweave_device_ready");
}

void loop() {
  delay(1000);
}
```

Create `firmware/include/config.example.h`:

```cpp
#pragma once

constexpr char WIFI_SSID[] = "replace-me";
constexpr char WIFI_PASSWORD[] = "replace-me";
constexpr char API_BASE_URL[] = "https://example.invalid";
constexpr char DEVICE_ID[] = "replace-me";
constexpr char DEVICE_SECRET[] = "replace-me";
```

The root `.gitignore` entry `firmware/include/config.h` ensures that the real local configuration is never committed.

Run:

```bash
cd firmware
pio test -e native
pio run -e esp32dev
```

Expected: test and firmware compilation pass.

- [ ] **Step 4: 记录 Arduino 兼容流程**

Create `firmware/README.md`:

````markdown
# ESP32 设备端

设备代码使用 Arduino Framework。为保证团队依赖和 CI 可复现，PlatformIO 是标准构建入口。

```bash
pio test -e native
pio run -e esp32dev
pio run -e esp32dev --target upload
pio device monitor
```

复制 `include/config.example.h` 为 `include/config.h` 并仅在本机填写凭据。`config.h` 不得提交。

当前编译基线是通用 `esp32dev`。确认实际 ESP32 板型后，须通过独立 PR 修改 `board`，并附一次真实烧录结果。
````

- [ ] **Step 5: 提交**

```bash
git add firmware
git commit -m "feat(firmware): scaffold esp32 arduino project"
```

---

### Task 7: 建立统一 CI 和最终验证

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: 四端各自的测试和构建命令。
- Produces: Pull Request 必须通过的后端、管理端、小程序和固件质量门禁。

- [ ] **Step 1: 添加 CI 工作流**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [master]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: travelweave_test
          POSTGRES_USER: travelweave
          POSTGRES_PASSWORD: travelweave_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U travelweave -d travelweave_test"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DJANGO_SETTINGS_MODULE: config.settings.test
      DJANGO_SECRET_KEY: ci-only-secret
      DATABASE_URL: postgresql://travelweave:travelweave_test@localhost:5432/travelweave_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: backend/requirements/*.txt
      - run: pip install -r backend/requirements/dev.txt
      - run: python backend/manage.py migrate --noinput
      - run: ruff check backend
      - run: ruff format --check backend
      - run: python backend/manage.py check
      - run: pytest backend -q

  admin-web:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: admin-web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "24"
          cache: npm
          cache-dependency-path: admin-web/package-lock.json
      - run: npm ci
      - run: npm test
      - run: npm run build

  miniprogram:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: miniprogram
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "24"
          cache: npm
          cache-dependency-path: miniprogram/package-lock.json
      - run: npm ci
      - run: npm test
      - run: npm run build:mp-weixin

  firmware:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: firmware
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install platformio
      - run: pio test -e native
      - run: pio run -e esp32dev
```

- [ ] **Step 2: 验证所有本地质量门禁**

Run:

```bash
cd backend
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python manage.py check
.venv/bin/pytest -q

cd ../admin-web
npm test
npm run build

cd ../miniprogram
npm test
npm run build:mp-weixin

cd ../firmware
pio test -e native
pio run -e esp32dev
```

Expected: every command exits 0.

- [ ] **Step 3: 验证仓库无敏感信息和意外产物**

Run:

```bash
git status --short
git ls-files | grep -E '(^|/)\.env$|config\.h$|node_modules|\.venv|\.pio' && exit 1 || true
git grep -nE 'WECHAT_APP_SECRET=.+|DIFY_API_KEY=.+|DEVICE_SECRET=.+|postgresql://[^:]+:[^@]+@' -- ':!*.example' && exit 1 || true
```

Expected: 没有真实 `.env`、设备 `config.h`、依赖目录、构建产物或疑似明文密钥被跟踪。

- [ ] **Step 4: 更新根 README 的启动命令**

Append to root `README.md`:

````markdown
## 本地启动

```bash
docker compose --env-file infra/.env.example -f infra/compose.yaml up -d postgres
cd backend && cp .env.example .env && .venv/bin/python manage.py migrate && .venv/bin/python manage.py runserver
cd admin-web && npm ci && npm run dev
cd miniprogram && npm ci && npm run dev:mp-weixin
cd firmware && pio run -e esp32dev
```

## 设计依据

- [产品与业务规则](docs/superpowers/specs/2026-07-13-jiang-an-mvp-product-business-design.md)
- [技术架构与数据设计](docs/superpowers/specs/2026-07-13-jiang-an-mvp-technical-architecture.md)
- [Web 管理端设计](docs/superpowers/specs/2026-07-21-admin-web-design.md)
- [v2 工程框架实施计划](docs/superpowers/plans/2026-07-21-v2-bootstrap-implementation-plan.md)
````

- [ ] **Step 5: 提交 CI**

```bash
git add .github README.md .gitignore
git commit -m "ci: add four-client quality gates"
```

- [ ] **Step 6: 最终分支检查**

Run:

```bash
git status --short
git log --oneline --decorate master..HEAD
git diff --check master...HEAD
```

Expected: working tree clean, only scoped v2 bootstrap commits are present, and `git diff --check` returns no whitespace errors.

- [ ] **Step 7: 推送并创建 Draft PR**

Run only after the user authorizes publication and local GitHub credentials have push permission:

```bash
git push -u origin chore/bootstrap-v2
```

Create a Draft PR titled `chore: bootstrap v2 four-client architecture`. The PR body must link the design specs, list all verification commands and state that business endpoints remain intentionally unimplemented until the API contract is approved.
