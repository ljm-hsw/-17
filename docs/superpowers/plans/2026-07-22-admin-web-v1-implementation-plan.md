# 游迹织梦后台管理系统前端 v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个使用真实 Django 管理 API、可供比赛展示和团队运营的 Vue 3 后台管理系统 v1。

**Architecture:** Django 继续作为唯一可信业务层，先补齐管理员认证和前端所需的读取契约；Vue 前端按 `services → stores/features → views/components` 分层。所有业务页面复用统一管理外壳、状态组件和高风险确认模式，页面不直接访问数据库或拼接接口。

**Tech Stack:** Django 5.2、Django REST Framework、SimpleJWT、pytest、Vue 3.5、TypeScript 5.8、Vite 7、Vue Router 4.5、Pinia 3、Fetch API、Element Plus 2.11、ECharts 6、Vitest 3.2。

## Global Constraints

- 目标分支固定为 `test`，不得合并到 `master`。
- 后台管理端只调用 `/api/v1/management/*` 和现有 `/api/v1/auth/refresh`，不得复用游客接口拼装敏感管理数据。
- 团队测试账号为 `demo_admin` / `TravelWeave-Demo-2026!`，仅允许在 `DEBUG=True` 的开发环境登录。
- 完整卡 UID、激活码历史明文、设备密钥和 JWT 不得进入普通页面、日志、测试快照或持久化业务状态。
- access 与 refresh token 首版存入 `sessionStorage`；关闭浏览器或退出登录时清理。
- 风险操作必须发送 `confirm: true` 和非空 `reason`，失败后不得自动重复提交。
- 视觉使用暖米白、江安绿和少量暖橙；正文对比度至少 4.5:1；功能图标使用统一 SVG 图标，不使用 emoji。
- 交互动画为 150–300ms，并尊重 `prefers-reduced-motion`。
- 支持 1440px、1024px、768px 和 375px 的降级布局；复杂数据表允许窄屏横向滚动。
- 本机 npm 命令使用 Node.js 24：`PATH=/opt/homebrew/opt/node@24/bin:$PATH`。
- PostgreSQL、Docker 和硬件端到端测试暂不作为本计划的阻塞项；轻量后端测试、前端测试、类型检查和构建必须通过。
- 每个功能遵循 TDD：先写失败测试，确认失败，再写最小实现，确认通过后提交。

## File Structure Map

```text
backend/
├── apps/accounts/management_auth.py        # 管理员登录与当前账号数据
├── apps/common/management_urls.py          # 管理 API 路由
├── apps/*/management_views.py              # 前端所需筛选与管理响应
├── apps/scenes/management/commands/
│   └── seed_jiang_an_demo.py               # Demo 管理员与业务演示数据
├── config/settings/base.py                 # Demo 管理员环境变量
└── tests/
    ├── test_management_auth.py
    ├── test_management_api.py
    └── test_demo_flow.py

admin-web/src/
├── components/
│   ├── layout/                             # AdminShell、侧边栏、顶部栏
│   ├── feedback/                           # 加载、空、错误、无权限状态
│   └── security/                           # 原因确认与一次性凭据弹窗
├── features/
│   ├── dashboard/
│   ├── content/                            # Scene、Spot、Route
│   ├── devices/
│   ├── cards/
│   ├── users/
│   └── records/                            # Visit、Checkin、Audit
├── services/
│   ├── http.ts
│   ├── tokenStorage.ts
│   ├── auth.ts
│   └── management/                         # 各领域 API 函数
├── stores/auth.ts
├── router/index.ts
├── types/                                  # API、认证和领域类型
├── styles/                                 # 设计 Token、全局与 Element 样式
└── views/                                  # 路由页面容器
```

---

### Task 1: 管理员认证与规范化 Demo 账号

**Files:**
- Create: `backend/apps/accounts/management_auth.py`
- Create: `backend/tests/test_management_auth.py`
- Modify: `backend/apps/common/management_urls.py`
- Modify: `backend/config/settings/base.py`
- Modify: `backend/apps/scenes/management/commands/seed_jiang_an_demo.py`
- Modify: `backend/.env.example`
- Modify: `backend/README.md`

**Interfaces:**
- Produces: `POST /api/v1/management/auth/login`，请求 `{username, password}`，返回 `{access, refresh, user}`。
- Produces: `GET /api/v1/management/auth/me`，返回 `ManagementUserData`。
- Produces: `management_user_data(user) -> dict`，字段为 `id, username, nickname, is_superuser, is_demo, permissions`。
- Produces: Settings `DEMO_ADMIN_USERNAME`, `DEMO_ADMIN_PASSWORD`, `DEMO_ADMIN_NICKNAME`。

- [ ] **Step 1: 写失败的管理认证测试**

```python
# backend/tests/test_management_auth.py
import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_staff_can_login_and_receive_permissions():
    api_client = APIClient()
    user = get_user_model().objects.create_superuser(
        username="demo_admin",
        password="TravelWeave-Demo-2026!",
        nickname="演示管理员",
        is_demo=True,
    )

    response = api_client.post(
        "/api/v1/management/auth/login",
        {"username": "demo_admin", "password": "TravelWeave-Demo-2026!"},
        format="json",
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["access"] and data["refresh"]
    assert data["user"]["id"] == str(user.id)
    assert data["user"]["is_superuser"] is True
    assert isinstance(data["user"]["permissions"], list)


@pytest.mark.django_db
def test_non_staff_cannot_use_management_login(user):
    api_client = APIClient()
    user.set_password("valid-password-2026")
    user.save(update_fields=("password",))
    response = api_client.post(
        "/api/v1/management/auth/login",
        {"username": user.username, "password": "valid-password-2026"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_demo_account_is_rejected_outside_debug():
    api_client = APIClient()
    get_user_model().objects.create_superuser(
        username="demo_admin",
        password="TravelWeave-Demo-2026!",
        is_demo=True,
    )
    response = api_client.post(
        "/api/v1/management/auth/login",
        {"username": "demo_admin", "password": "TravelWeave-Demo-2026!"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_demo_seed_creates_the_documented_staff_account(settings):
    from django.core.management import call_command

    settings.DEMO_ADMIN_USERNAME = "demo_admin"
    settings.DEMO_ADMIN_PASSWORD = "TravelWeave-Demo-2026!"
    settings.DEMO_ADMIN_NICKNAME = "演示管理员"
    call_command("seed_jiang_an_demo", device_secret="seed-device-secret")
    user = get_user_model().objects.get(username="demo_admin")
    assert user.is_staff and user.is_superuser and user.is_demo
    assert user.check_password("TravelWeave-Demo-2026!")
```

- [ ] **Step 2: 运行认证测试并确认失败**

Run: `DATABASE_URL=sqlite://:memory: .venv/bin/python -m pytest tests/test_management_auth.py -q`  
Expected: FAIL，登录 URL 返回 404。

- [ ] **Step 3: 实现管理员登录与当前账号接口**

```python
# backend/apps/accounts/management_auth.py
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.serializers import CharField, Serializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.api import api_response
from apps.common.schema import SchemaAPIView as APIView


class ManagementLoginSerializer(Serializer):
    username = CharField(max_length=150)
    password = CharField(max_length=128, trim_whitespace=False, write_only=True)


def management_user_data(user):
    return {
        "id": str(user.id),
        "username": user.username,
        "nickname": user.nickname,
        "is_superuser": user.is_superuser,
        "is_demo": user.is_demo,
        "permissions": sorted(user.get_all_permissions()),
    }


class ManagementLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ManagementLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request=request, **serializer.validated_data)
        if not user or not user.is_active or not user.is_staff:
            raise AuthenticationFailed("用户名或密码不正确")
        if user.is_demo and not settings.DEBUG:
            raise AuthenticationFailed("演示账号不能用于生产环境")
        refresh = RefreshToken.for_user(user)
        return api_response(
            request,
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": management_user_data(user),
            },
        )


class ManagementMeView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return api_response(request, management_user_data(request.user))
```

Add to `backend/apps/common/management_urls.py`:

```python
from apps.accounts.management_auth import ManagementLoginView, ManagementMeView

urlpatterns = [
    path("auth/login", ManagementLoginView.as_view()),
    path("auth/me", ManagementMeView.as_view()),
]
```

Insert these two entries at the beginning of the existing `urlpatterns` list; retain every existing management route after them.

- [ ] **Step 4: 配置并幂等创建 Demo 管理员**

Add to `backend/config/settings/base.py`:

```python
DEMO_ADMIN_USERNAME = env("DEMO_ADMIN_USERNAME", default="demo_admin")
DEMO_ADMIN_PASSWORD = env("DEMO_ADMIN_PASSWORD", default="TravelWeave-Demo-2026!")
DEMO_ADMIN_NICKNAME = env("DEMO_ADMIN_NICKNAME", default="演示管理员")
```

Add `User` import and call `_seed_demo_admin()` from the seed command. The method must be:

```python
from django.conf import settings
from apps.accounts.models import Card, CardActivationCode, User

def _seed_demo_admin(self):
    user, _ = User.objects.update_or_create(
        username=settings.DEMO_ADMIN_USERNAME,
        defaults={
            "nickname": settings.DEMO_ADMIN_NICKNAME,
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "is_demo": True,
        },
    )
    user.set_password(settings.DEMO_ADMIN_PASSWORD)
    user.save(update_fields=("password",))
```

Call `self._seed_demo_admin()` immediately before `self._seed_groups()` in `handle`. Extend `data_administrator` in `GROUP_MODELS` with `visits.visitsession` and `visits.checkinevent` so the later user/visit/checkin routes have explicit read permissions.

Document the three values in `backend/.env.example` and the command `python manage.py seed_jiang_an_demo` in `backend/README.md`, with an explicit development-only warning.

- [ ] **Step 5: 运行认证与演示数据测试**

Run: `DATABASE_URL=sqlite://:memory: .venv/bin/python -m pytest tests/test_management_auth.py tests/test_demo_flow.py -q`  
Expected: PASS，管理登录测试和原有 Demo 流程测试全部通过。

- [ ] **Step 6: 提交认证切片**

```bash
git add backend/apps/accounts/management_auth.py backend/apps/common/management_urls.py backend/config/settings/base.py backend/apps/scenes/management/commands/seed_jiang_an_demo.py backend/.env.example backend/README.md backend/tests/test_management_auth.py
git commit -m "feat(management): add admin login and demo account"
```

---

### Task 2: 补齐管理页面读取契约与服务端筛选

**Files:**
- Modify: `backend/apps/scenes/management_views.py`
- Modify: `backend/apps/accounts/management_views.py`
- Modify: `backend/apps/iot/management_views.py`
- Modify: `backend/apps/visits/management_views.py`
- Modify: `backend/apps/common/management.py`
- Modify: `backend/tests/test_management_api.py`

**Interfaces:**
- Produces: 完整 `SceneData`, `SpotData`, `DeviceData`, `VisitData`, `AuditData`。
- Produces: 列表筛选参数 `search`, `scene_id`, `spot_id`, `status`, `date_from`, `date_to`, `visit_id`。
- Produces: Dashboard 的趋势、排行和设备状态统一接受 `scene_id`, `date_from`, `date_to`。
- Consumes: Task 1 的 staff JWT，但测试继续可使用 `staff_client`。

- [ ] **Step 1: 写失败的完整字段与筛选测试**

Append to `backend/tests/test_management_api.py`:

```python
@pytest.mark.django_db
def test_management_scene_and_spot_details_include_editable_fields(staff_client, scene, spot):
    scene.map_image_url = "https://example.com/jiang-an.webp"
    scene.save(update_fields=("map_image_url",))
    response = staff_client.get(f"/api/v1/management/spots/{spot.id}")
    scene_response = staff_client.get(f"/api/v1/management/scenes/{scene.id}")
    assert scene_response.json()["data"]["map_image_url"].endswith("jiang-an.webp")
    assert response.json()["data"]["map_x"] == str(spot.map_x)
    assert response.json()["data"]["summary"] == spot.summary
    assert response.json()["data"]["tags"] == spot.tags
    assert isinstance(response.json()["data"]["media"], list)


@pytest.mark.django_db
def test_management_lists_apply_search_status_and_visit_filters(
    staff_client, accepted_event, scene
):
    devices = staff_client.get(
        f"/api/v1/management/devices?scene_id={scene.id}&search={accepted_event.device.device_id}"
    )
    events = staff_client.get(
        f"/api/v1/management/checkins?visit_id={accepted_event.visit_session_id}"
    )
    assert [row["id"] for row in devices.json()["data"]["items"]] == [
        str(accepted_event.device_id)
    ]
    assert [row["id"] for row in events.json()["data"]["items"]] == [
        str(accepted_event.id)
    ]


@pytest.mark.django_db
def test_dashboard_ranking_is_scoped_to_scene_and_date(staff_client, accepted_event, scene):
    response = staff_client.get(
        f"/api/v1/management/dashboard/spot-ranking?scene_id={scene.id}"
        f"&date_from={accepted_event.received_at.date()}"
        f"&date_to={accepted_event.received_at.date()}"
    )
    ids = [row["spot_id"] for row in response.json()["data"]["items"]]
    assert str(accepted_event.spot_id) in ids
```

- [ ] **Step 2: 运行新增管理测试并确认字段或筛选断言失败**

Run: `DATABASE_URL=sqlite://:memory: .venv/bin/python -m pytest tests/test_management_api.py -q`  
Expected: FAIL，缺少 `map_image_url`, `map_x`, `media` 或 `visit_id` 筛选。

- [ ] **Step 3: 扩展序列化函数并集中读取查询参数**

Implement the following exact additions:

```python
# backend/apps/scenes/management_views.py
def scene_data(scene):
    return {
        "id": str(scene.id),
        "slug": scene.slug,
        "name": scene.name,
        "subtitle": scene.subtitle,
        "timezone": scene.timezone,
        "map_image_url": scene.map_image_url,
        "status": scene.status,
    }


def spot_data(spot):
    return {
        "id": str(spot.id),
        "scene_id": str(spot.scene_id),
        "slug": spot.slug,
        "name": spot.name,
        "category": spot.category,
        "summary": spot.summary,
        "description": spot.description,
        "knowledge_content": spot.knowledge_content,
        "map_x": str(spot.map_x),
        "map_y": str(spot.map_y),
        "tags": spot.tags,
        "suggested_stay_minutes": spot.suggested_stay_minutes,
        "is_checkin_enabled": spot.is_checkin_enabled,
        "is_photo_spot": spot.is_photo_spot,
        "status": spot.status,
        "media": [media_data(item) for item in spot.media.order_by("sort_order", "id")],
    }
```

Also extend `binding_data(binding)` with `"unbound_reason": binding.unbound_reason`; this field is required by the historical binding drawer and remains non-sensitive.

Update Spot querysets with `prefetch_related("media")`. Apply the following exact filters only when the named query parameter is present:

| Endpoint | Query parameter | Django filter |
|---|---|---|
| Spots | `search` | `Q(name__icontains=value) | Q(slug__icontains=value)` |
| Spots | `scene_id`, `status` | exact fields with the same names |
| Routes | `search` | `Q(name__icontains=value) | Q(slug__icontains=value)` |
| Routes | `scene_id`, `status` | exact fields with the same names |
| Devices | `search` | `Q(device_id__icontains=value) | Q(firmware_version__icontains=value)` |
| Devices | `scene_id`, `spot_id`, `status` | exact fields with the same names |
| Cards | `search` | `Q(serial_no__icontains=value) | Q(uid_masked__icontains=value)` |
| Cards | `status` | exact field |
| Users | `search` | `Q(username__icontains=value) | Q(nickname__icontains=value)` |
| Users | `is_active`, `is_demo` | parse `true`/`false` then apply exact boolean fields |
| Visits | `scene_id`, `user_id` | exact fields |
| Visits | `date_from`, `date_to` | `local_date__gte`, `local_date__lte` |
| Checkins | `visit_id` | `visit_session_id` exact field |
| Checkins | `checkin_type` | exact field |

- [ ] **Step 4: Scope dashboard queries consistently**

Create and use this helper in `backend/apps/visits/management_views.py`:

```python
def dashboard_events(request):
    events = CheckinEvent.objects.filter(status=CheckinEvent.Status.ACCEPTED)
    if request.query_params.get("scene_id"):
        events = events.filter(spot__scene_id=request.query_params["scene_id"])
    if request.query_params.get("date_from"):
        events = events.filter(received_at__date__gte=request.query_params["date_from"])
    if request.query_params.get("date_to"):
        events = events.filter(received_at__date__lte=request.query_params["date_to"])
    return events
```

Use `dashboard_events(request)` in trend and ranking. Filter `DeviceStatusView` by `scene_id` when supplied. Add `actor_username` to `audit_data` using `log.actor.username` and update its queryset to `select_related("actor")`.

- [ ] **Step 5: 运行管理 API 回归测试**

Run: `DATABASE_URL=sqlite://:memory: .venv/bin/python -m pytest tests/test_management_api.py tests/test_management_mutations.py -q`  
Expected: PASS，读取契约与原有写入、审计、安全测试全部通过。

- [ ] **Step 6: 提交管理契约切片**

```bash
git add backend/apps/scenes/management_views.py backend/apps/accounts/management_views.py backend/apps/iot/management_views.py backend/apps/visits/management_views.py backend/apps/common/management.py backend/tests/test_management_api.py
git commit -m "feat(management): complete admin read contracts"
```

---

### Task 3: 前端 API 类型、Token 存储与 HTTP Client

**Files:**
- Create: `admin-web/src/types/api.ts`
- Create: `admin-web/src/types/auth.ts`
- Create: `admin-web/src/services/tokenStorage.ts`
- Create: `admin-web/src/services/http.ts`
- Create: `admin-web/src/services/auth.ts`
- Create: `admin-web/src/services/__tests__/http.spec.ts`
- Modify: `admin-web/src/services/api.ts`

**Interfaces:**
- Produces: `ApiEnvelope<T>`, `PageMeta`, `ApiClientError`。
- Produces: `tokenStorage.get/save/clear()`。
- Produces: `apiGet<T>`, `apiPost<TBody, TData>`, `apiPatch<TBody, TData>`。
- Produces: `login(username, password)`, `getManagementMe()`；token 刷新由 HTTP Client 内部统一执行。

- [ ] **Step 1: 写失败的解包、错误和刷新并发测试**

```ts
// admin-web/src/services/__tests__/http.spec.ts
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiClientError } from '../../types/api'
import { apiGet } from '../http'
import { tokenStorage } from '../tokenStorage'

describe('http client', () => {
  afterEach(() => {
    tokenStorage.clear()
    vi.restoreAllMocks()
  })

  it('unwraps data and preserves request id', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ data: { status: 'ok' }, request_id: 'req-1' }),
    }))
    await expect(apiGet<{ status: string }>('/api/v1/health')).resolves.toEqual({
      data: { status: 'ok' },
      requestId: 'req-1',
    })
  })

  it('normalizes backend failures', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({
        error: { code: 'PERMISSION_DENIED', message: '没有权限执行此操作', details: {} },
        request_id: 'req-403',
      }),
    }))
    await expect(apiGet('/api/v1/management/scenes')).rejects.toEqual(
      expect.objectContaining<ApiClientError>({ code: 'PERMISSION_DENIED', requestId: 'req-403' }),
    )
  })
})
```

- [ ] **Step 2: 运行 HTTP 测试并确认模块不存在**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/services/__tests__/http.spec.ts`  
Expected: FAIL，无法导入 `http` 或 `tokenStorage`。

- [ ] **Step 3: 实现类型和 sessionStorage Token 存储**

```ts
// admin-web/src/types/api.ts
export interface PageMeta { page: number; page_size: number; total: number }
export interface ApiEnvelope<T> { data: T; meta?: PageMeta; request_id: string }
export interface ApiFailure {
  error: { code: string; message: string; details: Record<string, string | string[]> }
  request_id: string
}
export interface ApiResult<T> { data: T; meta?: PageMeta; requestId: string }

export class ApiClientError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
    public details: Record<string, string | string[]> = {},
    public requestId = '',
  ) { super(message) }
}

// admin-web/src/services/tokenStorage.ts
const ACCESS_KEY = 'travelweave.management.access'
const REFRESH_KEY = 'travelweave.management.refresh'
export const tokenStorage = {
  get: () => ({
    access: sessionStorage.getItem(ACCESS_KEY),
    refresh: sessionStorage.getItem(REFRESH_KEY),
  }),
  save: (access: string, refresh: string) => {
    sessionStorage.setItem(ACCESS_KEY, access)
    sessionStorage.setItem(REFRESH_KEY, refresh)
  },
  saveAccess: (access: string) => sessionStorage.setItem(ACCESS_KEY, access),
  clear: () => {
    sessionStorage.removeItem(ACCESS_KEY)
    sessionStorage.removeItem(REFRESH_KEY)
  },
}
```

- [ ] **Step 4: 实现 HTTP 请求、统一错误和单次刷新队列**

Implement `http.ts` with this exact transport and refresh flow:

```ts
import type { ApiEnvelope, ApiFailure, ApiResult } from '../types/api'
import { ApiClientError } from '../types/api'
import { tokenStorage } from './tokenStorage'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
let refreshPromise: Promise<string> | null = null

async function parseFailure(response: Response): Promise<ApiClientError> {
  const payload = (await response.json()) as ApiFailure
  return new ApiClientError(
    payload.error.code,
    payload.error.message,
    response.status,
    payload.error.details,
    payload.request_id,
  )
}

async function refreshAccess(): Promise<string> {
  if (refreshPromise) return refreshPromise
  refreshPromise = (async () => {
    const refresh = tokenStorage.get().refresh
    if (!refresh) throw new ApiClientError('AUTH_REQUIRED', '请重新登录', 401)
    const response = await fetch(`${apiBaseUrl}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    })
    if (!response.ok) throw await parseFailure(response)
    const payload = (await response.json()) as ApiEnvelope<{ access: string }>
    tokenStorage.saveAccess(payload.data.access)
    return payload.data.access
  })()
  try {
    return await refreshPromise
  } catch (error) {
    tokenStorage.clear()
    throw error
  } finally {
    refreshPromise = null
  }
}

async function apiRequest<T>(
  path: string,
  init: RequestInit,
  allowRetry: boolean,
  retried = false,
): Promise<ApiResult<T>> {
  const access = tokenStorage.get().access
  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  if (access) headers.set('Authorization', `Bearer ${access}`)
  let response: Response
  try {
    response = await fetch(`${apiBaseUrl}${path}`, { ...init, headers })
  } catch {
    throw new ApiClientError('NETWORK_ERROR', '网络连接失败，请稍后重试', 0)
  }
  if (response.status === 401 && allowRetry && !retried && tokenStorage.get().refresh) {
    const renewed = await refreshAccess()
    headers.set('Authorization', `Bearer ${renewed}`)
    return apiRequest<T>(path, { ...init, headers }, allowRetry, true)
  }
  if (!response.ok) throw await parseFailure(response)
  const payload = (await response.json()) as ApiEnvelope<T>
  return { data: payload.data, meta: payload.meta, requestId: payload.request_id }
}

export const apiGet = <T>(path: string) => apiRequest<T>(path, { method: 'GET' }, true)
export const apiPost = <TBody, TData>(path: string, body: TBody, allowRetry = true) =>
  apiRequest<TData>(path, { method: 'POST', body: JSON.stringify(body) }, allowRetry)
export const apiPatch = <TBody, TData>(path: string, body: TBody, allowRetry = true) =>
  apiRequest<TData>(path, { method: 'PATCH', body: JSON.stringify(body) }, allowRetry)
```

When parsing a failed response, construct `ApiClientError(payload.error.code, payload.error.message, response.status, payload.error.details, payload.request_id)`. Clear tokens when refresh fails.

- [ ] **Step 5: 实现认证领域服务并迁移健康检查**

```ts
// admin-web/src/types/auth.ts
export interface ManagementUser {
  id: string
  username: string
  nickname: string
  is_superuser: boolean
  is_demo: boolean
  permissions: string[]
}
export interface TokenPair { access: string; refresh: string }
export interface LoginResult extends TokenPair { user: ManagementUser }

// admin-web/src/services/auth.ts
import { apiGet, apiPost } from './http'
import type { LoginResult, ManagementUser } from '../types/auth'
export const login = (username: string, password: string) =>
  apiPost<{ username: string; password: string }, LoginResult>(
    '/api/v1/management/auth/login', { username, password }, false,
  )
export const getManagementMe = () =>
  apiGet<ManagementUser>('/api/v1/management/auth/me')
```

Update `getBackendHealth` to call `apiGet<{status: 'ok'}>` and return `result.data.status`.

- [ ] **Step 6: 运行服务测试、类型检查并提交**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/services/__tests__/http.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS。

```bash
git add admin-web/src/types admin-web/src/services
git commit -m "feat(admin-web): add typed API client"
```

---

### Task 4: Auth Store、登录页和权限路由

**Files:**
- Create: `admin-web/src/stores/auth.ts`
- Create: `admin-web/src/views/LoginView.vue`
- Create: `admin-web/src/views/ForbiddenView.vue`
- Create: `admin-web/src/views/NotFoundView.vue`
- Create: `admin-web/src/stores/__tests__/auth.spec.ts`
- Create: `admin-web/src/router/__tests__/guards.spec.ts`
- Modify: `admin-web/src/router/index.ts`
- Modify: `admin-web/src/App.vue`
- Modify: `admin-web/src/main.ts`

**Interfaces:**
- Produces: `useAuthStore()` with `user`, `isAuthenticated`, `login`, `restore`, `logout`, `can(permission)`。
- Produces: route meta `requiresAuth?: boolean`, `permission?: string`。
- Consumes: Task 3 `login`, `getManagementMe`, `tokenStorage`。

- [ ] **Step 1: 写失败的 Store 与路由守卫测试**

```ts
// admin-web/src/stores/__tests__/auth.spec.ts
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../../services/auth'
import { useAuthStore } from '../auth'

describe('auth store', () => {
  beforeEach(() => {
    sessionStorage.clear()
    setActivePinia(createPinia())
  })
  it('stores the management user after login', async () => {
    vi.spyOn(authApi, 'login').mockResolvedValue({
      data: {
        access: 'access', refresh: 'refresh',
        user: { id: '1', username: 'demo_admin', nickname: '演示管理员', is_superuser: true, is_demo: true, permissions: [] },
      }, requestId: 'req-login',
    })
    const store = useAuthStore()
    await store.login('demo_admin', 'TravelWeave-Demo-2026!')
    expect(store.isAuthenticated).toBe(true)
    expect(store.user?.username).toBe('demo_admin')
  })
})
```

The guard test must assert an unauthenticated navigation to `/devices` redirects to `/login?redirect=/devices`, and a staff user without the route permission redirects to `/403`.

- [ ] **Step 2: 运行测试并确认 Store 和路由行为缺失**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/stores/__tests__/auth.spec.ts src/router/__tests__/guards.spec.ts`  
Expected: FAIL，Store 或路由守卫模块不存在。

- [ ] **Step 3: 实现 Auth Store**

The Store must save tokens only through `tokenStorage`, expose user through a `ref<ManagementUser | null>`, and implement permissions as:

```ts
const can = (permission?: string) => {
  if (!permission) return true
  if (user.value?.is_superuser) return true
  return user.value?.permissions.includes(permission) ?? false
}
```

`restore()` returns early when no access token exists; otherwise it calls `getManagementMe()`. Any restore failure calls `logout()`.

- [ ] **Step 4: 实现登录页与路由守卫**

`LoginView.vue` contains labeled username/password fields, submit loading state, a development-account note, and `data-test="login-submit"`. It calls `auth.login`, then routes to the validated `redirect` query value or `/dashboard`. It displays `ApiClientError.message` without clearing either input.

Router rules:

```ts
{ path: '/login', name: 'login', component: LoginView }
{ path: '/403', name: 'forbidden', component: ForbiddenView }
{ path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView }
```

The global guard restores the session once, redirects anonymous protected routes to login, redirects authenticated users without `meta.permission` to `/403`, and redirects an authenticated `/login` visit to `/dashboard`.

- [ ] **Step 5: 注册 Pinia、Element Plus 并运行测试**

`main.ts` must create the app once, register `createPinia()`, router and Element Plus, then mount `#app`.

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/stores/__tests__/auth.spec.ts src/router/__tests__/guards.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS。

- [ ] **Step 6: 提交登录与权限切片**

```bash
git add admin-web/src/stores admin-web/src/router admin-web/src/views/LoginView.vue admin-web/src/views/ForbiddenView.vue admin-web/src/views/NotFoundView.vue admin-web/src/App.vue admin-web/src/main.ts
git commit -m "feat(admin-web): add management authentication"
```

---

### Task 5: 设计 Token、管理外壳与通用反馈/安全组件

**Files:**
- Modify: `admin-web/package.json`
- Modify: `admin-web/package-lock.json`
- Create: `admin-web/src/styles/tokens.css`
- Create: `admin-web/src/styles/element.css`
- Create: `admin-web/src/components/layout/AdminShell.vue`
- Create: `admin-web/src/components/layout/AppSidebar.vue`
- Create: `admin-web/src/components/layout/AppHeader.vue`
- Create: `admin-web/src/components/feedback/PageState.vue`
- Create: `admin-web/src/components/security/ConfirmReasonDialog.vue`
- Create: `admin-web/src/components/security/OneTimeSecretDialog.vue`
- Create: `admin-web/src/types/content.ts`
- Create: `admin-web/src/services/management/content.ts`
- Create: `admin-web/src/stores/scene.ts`
- Create: `admin-web/src/components/__tests__/shared-components.spec.ts`
- Modify: `admin-web/src/style.css`
- Modify: `admin-web/src/router/index.ts`

**Interfaces:**
- Produces: `AdminShell` with nested `<RouterView />`。
- Produces: `PageState` props `status`, `title`, `description`, `requestId` and event `retry`。
- Produces: `ConfirmReasonDialog` v-model and event `confirm({confirm: true, reason})`。
- Produces: `OneTimeSecretDialog` props `modelValue`, `label`, `secret` and `close` confirmation。
- Produces: `useSceneStore()` with `scenes`, `currentSceneId`, `currentScene`, `loadScenes()`, `selectScene(id)`。

- [ ] **Step 1: 写失败的共享组件测试**

```ts
// admin-web/src/components/__tests__/shared-components.spec.ts
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ConfirmReasonDialog from '../security/ConfirmReasonDialog.vue'
import PageState from '../feedback/PageState.vue'

describe('shared management components', () => {
  it('does not confirm a risk action without a reason', async () => {
    const wrapper = mount(ConfirmReasonDialog, { props: { modelValue: true, title: '强制解绑' } })
    await wrapper.get('[data-test="confirm-risk"]').trigger('click')
    expect(wrapper.emitted('confirm')).toBeUndefined()
  })
  it('renders failure separately from empty data', () => {
    const wrapper = mount(PageState, { props: { status: 'error', title: '加载失败', requestId: 'req-1' } })
    expect(wrapper.text()).toContain('加载失败')
    expect(wrapper.text()).toContain('req-1')
  })
})
```

- [ ] **Step 2: 运行组件测试并确认失败**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/components/__tests__/shared-components.spec.ts`  
Expected: FAIL，共享组件不存在。

- [ ] **Step 3: 定义全局视觉 Token 与基础可访问性**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm install @element-plus/icons-vue@^2.3.2`  
Expected: `package.json` adds a direct production dependency and `package-lock.json` remains consistent.

Define these exact CSS variables in `tokens.css`:

```css
:root {
  --tw-color-primary: #2f8066;
  --tw-color-primary-dark: #173f35;
  --tw-color-accent: #c76a32;
  --tw-color-bg: #f6f4ee;
  --tw-color-surface: #ffffff;
  --tw-color-text: #183c32;
  --tw-color-muted: #60736c;
  --tw-color-border: #dfe7e2;
  --tw-radius-sm: 8px;
  --tw-radius-md: 12px;
  --tw-radius-lg: 18px;
  --tw-shadow-card: 0 8px 24px rgb(31 66 53 / 8%);
  --tw-sidebar-width: 240px;
  --tw-motion-fast: 180ms;
}
```

`style.css` imports both style files, sets `box-sizing`, body background/text/font, visible `:focus-visible`, button cursor, and reduced-motion overrides.

Create `Scene` in `types/content.ts` with `id, slug, name, subtitle, timezone, map_image_url, status`. Create `listScenes()` in `services/management/content.ts`. `useSceneStore.loadScenes()` loads that list and selects the first Scene only when no saved ID exists; `selectScene` writes the ID to `sessionStorage` key `travelweave.management.scene`.

- [ ] **Step 4: 实现管理外壳与业务导航**

Sidebar groups and routes are fixed to the approved information architecture. Each item carries `permission?: string`; unavailable Photos/AI is rendered as disabled text with “规划中”, not as a link. Header reads and updates `useSceneStore`, shows `测试环境`, demo-mode button and account menu. At widths below 768px, sidebar becomes an Element Plus drawer.

- [ ] **Step 5: 实现反馈和安全组件**

`PageState` supports exactly `loading | empty | no-results | error | forbidden`. `ConfirmReasonDialog` uses a labeled textarea, rejects trimmed empty reason, disables its button during `submitting`, and emits `{confirm: true, reason: reason.trim()}`. `OneTimeSecretDialog` uses `navigator.clipboard.writeText(secret)`, shows “关闭后无法再次查看”, and requires the checkbox “我已安全保存” before closing.

- [ ] **Step 6: 运行组件测试、类型检查并提交**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/components/__tests__/shared-components.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS。

```bash
git add admin-web/package.json admin-web/package-lock.json admin-web/src/styles admin-web/src/components admin-web/src/types/content.ts admin-web/src/services/management/content.ts admin-web/src/stores/scene.ts admin-web/src/style.css admin-web/src/router/index.ts
git commit -m "feat(admin-web): add admin shell and shared UX"
```

---

### Task 6: 真实数据展示看板

**Files:**
- Create: `admin-web/src/types/dashboard.ts`
- Create: `admin-web/src/services/management/dashboard.ts`
- Create: `admin-web/src/features/dashboard/useDashboard.ts`
- Create: `admin-web/src/features/dashboard/MetricCard.vue`
- Create: `admin-web/src/features/dashboard/CheckinTrendChart.vue`
- Create: `admin-web/src/features/dashboard/SpotRanking.vue`
- Create: `admin-web/src/features/dashboard/LatestEvents.vue`
- Create: `admin-web/src/features/dashboard/DeviceStatusPanel.vue`
- Create: `admin-web/src/stores/display.ts`
- Modify: `admin-web/src/views/DashboardView.vue`
- Modify: `admin-web/src/views/__tests__/DashboardView.spec.ts`

**Interfaces:**
- Produces: dashboard service functions `getSummary`, `getTrend`, `getSpotRanking`, `getLatestEvents`, `getDeviceStatus`。
- Produces: `useDashboard(filters)` with independent module states and `refreshAll()`。
- Produces: `useDisplayStore()` with `isDemoMode`, `enterDemoMode()`, `exitDemoMode()`；`AdminShell` 根据该状态隐藏写入导航。
- Consumes: Task 3 HTTP client and Task 5 feedback/layout components。

- [ ] **Step 1: 将健康检查测试替换为真实看板失败测试**

Mock the five dashboard service functions. Assert the page renders `today_visitors`, `accepted_checkins`, `online_devices`, `bound_cards`, the `generated_at` update label, and one event. Add a second test where ranking rejects with `ApiClientError` and assert summary still renders while only ranking shows its error state.

- [ ] **Step 2: 运行看板测试并确认旧健康页不满足断言**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/views/__tests__/DashboardView.spec.ts`  
Expected: FAIL，页面仍只显示后端健康状态。

- [ ] **Step 3: 实现看板类型与领域 Service**

Define exact summary fields matching the backend: `generated_at`, `scene_id`, `date_from`, `date_to`, `today_visitors`, `accepted_checkins`, `bound_cards`, `online_devices`. Each service builds query parameters with `URLSearchParams` and calls its matching `/api/v1/management/dashboard/*` endpoint.

- [ ] **Step 4: 实现独立模块加载和轮询**

`useDashboard` must load modules with separate error refs so one rejection cannot clear successful data. Start summary/device polling every 10 seconds and latest-events polling every 5 seconds in `onMounted`; clear both timers in `onUnmounted`. Manual refresh calls all loaders. Do not count a failed module as zero.

- [ ] **Step 5: 实现看板视觉与演示模式**

Use four `MetricCard`s, an ECharts line chart, spot ranking, latest event list and device status panel. Display definition text below each metric. The page header shows Scene/date filters, “最后更新” and manual refresh. `useDisplayStore.enterDemoMode()` sets `isDemoMode=true` and calls `document.documentElement.requestFullscreen()` when available; `exitDemoMode()` resets the flag and calls `document.exitFullscreen()` when active. `AdminShell` hides write-oriented navigation while the flag is true without changing permission data.

- [ ] **Step 6: 运行测试、构建并提交**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/views/__tests__/DashboardView.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run build`  
Expected: PASS and `dist/` generated。

```bash
git add admin-web/src/types/dashboard.ts admin-web/src/services/management/dashboard.ts admin-web/src/features/dashboard admin-web/src/stores/display.ts admin-web/src/views/DashboardView.vue admin-web/src/views/__tests__/DashboardView.spec.ts admin-web/src/components/layout/AdminShell.vue
git commit -m "feat(admin-web): build live operations dashboard"
```

---

### Task 7: 场景、点位与路线内容运营

**Files:**
- Modify: `admin-web/src/types/content.ts`
- Modify: `admin-web/src/services/management/content.ts`
- Create: `admin-web/src/features/content/SceneMapPanel.vue`
- Create: `admin-web/src/features/content/SpotFormDrawer.vue`
- Create: `admin-web/src/features/content/SpotMediaList.vue`
- Create: `admin-web/src/features/content/RouteFormDrawer.vue`
- Create: `admin-web/src/views/ScenesView.vue`
- Create: `admin-web/src/views/SpotsView.vue`
- Create: `admin-web/src/views/RoutesView.vue`
- Create: `admin-web/src/features/content/__tests__/content.spec.ts`
- Modify: `admin-web/src/router/index.ts`

**Interfaces:**
- Produces: `listScenes`, `getScene`, `updateScene`, `listSpots`, `createSpot`, `updateSpot`, `publishSpot`, `disableSpot`, `createSpotMedia`, `updateSpotMedia`, `disableSpotMedia`, `listRoutes`, `createRoute`, `updateRoute`。
- Consumes: `ConfirmReasonDialog`, `PageState`, typed HTTP functions。

- [ ] **Step 1: 写失败的点位表单与风险停用测试**

Test that `SpotFormDrawer` emits a payload containing `scene_id, slug, name, category, summary, description, knowledge_content, map_x, map_y, tags, suggested_stay_minutes, is_checkin_enabled, is_photo_spot, status`. Test that clicking disable opens `ConfirmReasonDialog` and sends `{confirm: true, reason}` to the service.

- [ ] **Step 2: 运行内容运营测试并确认失败**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/content/__tests__/content.spec.ts`  
Expected: FAIL，内容模块不存在。

- [ ] **Step 3: 实现内容类型和 API Service**

Use backend names verbatim. `map_x` and `map_y` are strings in response and form payload. `Route.stops` is `{spot_id: string; order: number; note: string}[]`. Disable functions call `apiPost` with `allowRetry=false`.

- [ ] **Step 4: 实现场景地图和点位运营页**

Scene page renders `map_image_url` with spot pins positioned by `left: calc(map_x * 100%)` and `top: calc(map_y * 100%)`; coordinates outside `[0,1]` show a validation error before save. Spots page supplies server-side Scene/status/search filters, paginated table, full edit drawer, publish action, risk disable and media list. Media creation accepts URL/storage key metadata only because binary upload is not part of the current backend API.

- [ ] **Step 5: 实现路线编排页**

Route form allows adding each Scene Spot once, moving rows up/down, deleting rows and editing notes. Before submit, normalize order to 1-based consecutive integers. Disable submit when no stop exists or duplicate Spot IDs are present.

- [ ] **Step 6: 注册路由并验证**

Register `/scenes`, `/spots`, `/routes` under `AdminShell` with exact permission meta `scenes.view_scene`, `scenes.view_spot`, and `scenes.view_route`. Run:

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/content/__tests__/content.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS。

- [ ] **Step 7: 提交内容运营切片**

```bash
git add admin-web/src/types/content.ts admin-web/src/services/management/content.ts admin-web/src/features/content admin-web/src/views/ScenesView.vue admin-web/src/views/SpotsView.vue admin-web/src/views/RoutesView.vue admin-web/src/router/index.ts
git commit -m "feat(admin-web): add scene spot and route operations"
```

---

### Task 8: 设备管理与一次性密钥

**Files:**
- Create: `admin-web/src/types/device.ts`
- Create: `admin-web/src/services/management/devices.ts`
- Create: `admin-web/src/features/devices/DeviceFormDrawer.vue`
- Create: `admin-web/src/features/devices/DeviceDetailDrawer.vue`
- Create: `admin-web/src/views/DevicesView.vue`
- Create: `admin-web/src/features/devices/__tests__/devices.spec.ts`
- Modify: `admin-web/src/router/index.ts`

**Interfaces:**
- Produces: `listDevices`, `getDevice`, `createDevice`, `updateDevice`, `rotateDeviceSecret`, `listDeviceCheckins`。
- Produces: `DeviceSecretResult` containing regular Device fields plus `device_secret` only on create/rotation。

- [ ] **Step 1: 写失败的设备创建和密钥轮换测试**

Test that successful create opens `OneTimeSecretDialog` with the returned `device_secret`, while later detail rendering contains only `secret_fingerprint`. Test that rotation cannot call its service before reason confirmation and passes `allowRetry=false` through the domain service.

- [ ] **Step 2: 运行设备测试并确认失败**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/devices/__tests__/devices.spec.ts`  
Expected: FAIL，设备模块不存在。

- [ ] **Step 3: 实现设备 API 与类型**

Device fields exactly match backend: `id, device_id, scene_id, spot_id, device_type, secret_fingerprint, status, firmware_version, last_seen_at, last_error_code`. Create payload requires `device_id, scene_id, spot_id, device_type`; update may include status and firmware version. Rotation payload is `{confirm: true, reason: string}` and uses `allowRetry=false`.

- [ ] **Step 4: 实现列表、详情和表单**

Devices page provides Scene/Spot/status/search filters and status text plus icon. Online means active device with `last_seen_at` within 120 seconds; status display must still distinguish disabled from offline. Detail drawer shows masked fingerprint, recent events, last error and firmware. Changing Scene clears an incompatible Spot selection.

- [ ] **Step 5: 实现一次性密钥流程并验证**

After create or rotation, keep the secret only in a local component ref passed to `OneTimeSecretDialog`; set that ref to an empty string on close. Do not store it in Pinia or console output.

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/devices/__tests__/devices.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS。

Register `/devices` under `AdminShell` with permission meta `iot.view_device`.

- [ ] **Step 6: 提交设备切片**

```bash
git add admin-web/src/types/device.ts admin-web/src/services/management/devices.ts admin-web/src/features/devices admin-web/src/views/DevicesView.vue admin-web/src/router/index.ts
git commit -m "feat(admin-web): add device operations"
```

---

### Task 9: 卡片、批量导入与一次性激活码

**Files:**
- Create: `admin-web/src/types/card.ts`
- Create: `admin-web/src/services/management/cards.ts`
- Create: `admin-web/src/features/cards/CardFormDrawer.vue`
- Create: `admin-web/src/features/cards/CardImportDialog.vue`
- Create: `admin-web/src/features/cards/CardDetailDrawer.vue`
- Create: `admin-web/src/views/CardsView.vue`
- Create: `admin-web/src/features/cards/__tests__/cards.spec.ts`
- Modify: `admin-web/src/router/index.ts`

**Interfaces:**
- Produces: `listCards`, `getCard`, `createCard`, `previewCardImport`, `confirmCardImport`, `createActivationCode`, `listCardBindings`, `listCardCheckins`。
- Produces: `ImportPreview` with `valid`, `duplicate`, `invalid` arrays。

- [ ] **Step 1: 写失败的导入预览和激活码测试**

Test that import confirm remains disabled when preview contains duplicate or invalid rows. Test that successful activation-code creation opens `OneTimeSecretDialog`, displays `activation_code`, and clears it when the dialog closes.

- [ ] **Step 2: 运行卡片测试并确认失败**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/cards/__tests__/cards.spec.ts`  
Expected: FAIL，卡片模块不存在。

- [ ] **Step 3: 实现卡片类型和 API Service**

Card response fields are `id, serial_no, uid_masked, status, issued_at, last_used_at`. Raw `card_uid` is accepted only in create/import request types and must never appear in response types. `confirmCardImport` and `createActivationCode` use `allowRetry=false`.

- [ ] **Step 4: 实现卡片列表、详情与批量导入**

Cards page shows masked UID, status, active binding and last use. Import dialog accepts pasted CSV-like lines `serial_no,card_uid`, parses them into rows locally, calls preview, and renders valid/duplicate/invalid groups before confirm. Confirm sends the original rows only after a clean preview and explicit checkbox confirmation.

- [ ] **Step 5: 实现激活码一次性显示并验证**

The plaintext activation code lives only in a local ref. The detail API response and binding list never attempt to recover it. Run:

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/cards/__tests__/cards.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS。

Register `/cards` under `AdminShell` with permission meta `accounts.view_card`.

- [ ] **Step 6: 提交卡片切片**

```bash
git add admin-web/src/types/card.ts admin-web/src/services/management/cards.ts admin-web/src/features/cards admin-web/src/views/CardsView.vue admin-web/src/router/index.ts
git commit -m "feat(admin-web): add card and activation operations"
```

---

### Task 10: 用户、卡片绑定追踪与强制解绑

**Files:**
- Create: `admin-web/src/types/user.ts`
- Create: `admin-web/src/services/management/users.ts`
- Create: `admin-web/src/features/users/UserDetailDrawer.vue`
- Create: `admin-web/src/views/UsersView.vue`
- Create: `admin-web/src/features/users/__tests__/users.spec.ts`
- Modify: `admin-web/src/router/index.ts`

**Interfaces:**
- Produces: `listUsers`, `getUser`, `listUserCards`, `listUserVisits`, `listUserCheckins`, `forceUnbind`。
- Consumes: Task 5 `ConfirmReasonDialog` and Task 9 masked card types。

- [ ] **Step 1: 写失败的脱敏显示与强制解绑测试**

Test that user list renders nickname/username, `active_card_count` and demo status but never renders `wechat_openid`. Test that force unbind is not submitted without a non-empty reason and refreshes only the current user drawer after success.

- [ ] **Step 2: 运行用户测试并确认失败**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/users/__tests__/users.spec.ts`  
Expected: FAIL，用户模块不存在。

- [ ] **Step 3: 实现用户 API 和详情聚合**

Keep endpoints independent in the service. `UserDetailDrawer` loads user, cards, visits and recent checkins with `Promise.allSettled`; each section owns its error state so one failed association does not hide the others. Binding fields are `id, user_id, card_id, alias, is_primary, bind_method, bound_at, unbound_at, unbound_reason` plus nested masked card fields returned by backend.

- [ ] **Step 4: 实现强制解绑风险操作**

Only active bindings show “强制解绑”. Submit `apiPost('/api/v1/management/bindings/{id}/force-unbind', {confirm: true, reason}, false)`. On success, reload that user’s card section and show a success message; never delete the historical binding row locally.

Register `/users` under `AdminShell` with permission meta `accounts.view_cardbinding`.

- [ ] **Step 5: 运行测试、类型检查并提交**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/users/__tests__/users.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS。

```bash
git add admin-web/src/types/user.ts admin-web/src/services/management/users.ts admin-web/src/features/users admin-web/src/views/UsersView.vue admin-web/src/router/index.ts
git commit -m "feat(admin-web): add user and binding traceability"
```

---

### Task 11: 游览、打卡和只读审计

**Files:**
- Create: `admin-web/src/types/records.ts`
- Create: `admin-web/src/services/management/records.ts`
- Create: `admin-web/src/features/records/VisitDetailDrawer.vue`
- Create: `admin-web/src/features/records/CheckinDetailDrawer.vue`
- Create: `admin-web/src/views/VisitsView.vue`
- Create: `admin-web/src/views/CheckinsView.vue`
- Create: `admin-web/src/views/AuditLogsView.vue`
- Create: `admin-web/src/features/records/__tests__/records.spec.ts`
- Modify: `admin-web/src/router/index.ts`

**Interfaces:**
- Produces: `listVisits`, `getVisit`, `listCheckins`, `getCheckin`, `listAuditLogs`。
- Consumes: Task 2 date/Scene/visit filters and enriched audit data。

- [ ] **Step 1: 写失败的跨对象追踪和审计只读测试**

Test that selecting a visit loads checkins with `visit_id`, displays event order by `received_at`, and links to user/card/spot/device filters. Test that Audit page has no create, edit or delete button and displays `actor_username`, `action`, target, reason, request ID and time.

- [ ] **Step 2: 运行记录测试并确认失败**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/records/__tests__/records.spec.ts`  
Expected: FAIL，记录模块不存在。

- [ ] **Step 3: 实现记录类型和 API Service**

Use backend names without aliases. Checkin fields are `id, event_id, device_id, spot_id, user_id, card_id, visit_id, checkin_type, status, failure_code, received_at`. Audit fields are `id, actor_id, actor_username, actor_role, action, target_type, target_id, before, after, reason, request_id, created_at`.

- [ ] **Step 4: 实现游览与打卡页面**

Visits supports Scene/user filters and paginated detail. Detail drawer loads related checkins using `visit_id`; accepted, rejected and duplicate/failure conditions use text plus icon, never color alone. Checkins supports Scene/date/status/Spot/Device/Card/User filters and preserves filter query in the URL so cross-page trace links are shareable.

- [ ] **Step 5: 实现审计页与 JSON 差异展示**

Audit table is read-only. Expand rows to render `before` and `after` as formatted JSON with HTML escaping; do not interpret sensitive values. Add “复制 request_id” using Clipboard API. No mutation service function exists for Audit.

Register `/visits` with `visits.view_visitsession`, `/checkins` with `visits.view_checkinevent`, and `/audit-logs` as staff-authenticated without an additional model permission because the current backend endpoint is read-only `IsAdminUser`.

- [ ] **Step 6: 运行测试、类型检查并提交**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/features/records/__tests__/records.spec.ts`  
Expected: PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS。

```bash
git add admin-web/src/types/records.ts admin-web/src/services/management/records.ts admin-web/src/features/records admin-web/src/views/VisitsView.vue admin-web/src/views/CheckinsView.vue admin-web/src/views/AuditLogsView.vue admin-web/src/router/index.ts
git commit -m "feat(admin-web): add visit checkin and audit views"
```

---

### Task 12: 全流程联调、响应式、无障碍与团队运行文档

**Files:**
- Create: `admin-web/src/__tests__/management-flow.spec.ts`
- Modify: `admin-web/README.md`
- Modify: `README.md`
- Modify: `admin-web/.env.example`
- Modify: `docs/superpowers/specs/2026-07-22-admin-web-v1-design.md` only if implementation reveals a factual contract correction

**Interfaces:**
- Consumes: Tasks 1–11 complete management flow。
- Produces: reproducible local runbook and final verification evidence。

- [ ] **Step 1: 写失败的前端管理主流程测试**

Create a service-mocked integration test that mounts the real router and Pinia, logs in, visits dashboard, opens a device, confirms a secret rotation, visits a user, confirms force-unbind, and opens the audit list. Assert every high-risk payload contains `confirm: true` and its typed reason, and assert the one-time secret disappears after close.

- [ ] **Step 2: 运行主流程测试并修复仅由集成暴露的连接错误**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test -- src/__tests__/management-flow.spec.ts`  
Expected before final wiring: FAIL on a missing route/service connection。  
Implement only the missing imports, route registrations or prop/event connections identified by this test; do not add new product features.

- [ ] **Step 3: 完成响应式和可访问性检查**

Verify these exact conditions in browser devtools: 1440px full sidebar and two-column dashboard; 1024px readable tables; 768px drawer sidebar; 375px login and confirmations without unreachable controls. Keyboard-tab through login, sidebar, filters, drawers and dialogs. Confirm visible focus, labeled form controls, icon button aria-labels, no color-only status, and reduced-motion CSS.

- [ ] **Step 4: 编写团队运行与测试账号文档**

`admin-web/README.md` must include:

```text
Node.js: 24 LTS
Backend: http://localhost:8000
Frontend: http://localhost:5173
Demo username: demo_admin
Demo password: TravelWeave-Demo-2026!
Restriction: local DEBUG environment only; production rejects this account
Commands: npm ci, npm run dev, npm test, npm run type-check, npm run build
```

Root README adds the ordered startup flow: configure backend env, migrate, seed demo data, start Django, configure `VITE_API_BASE_URL`, start admin web.

- [ ] **Step 5: 运行完整轻量后端验证**

Run: `DATABASE_URL=sqlite://:memory: .venv/bin/python -m pytest -q -k 'not test_v2_is_configured_for_postgresql'`  
Expected: all selected tests PASS。  
Run: `.venv/bin/python -m pytest tests/test_database_vendor.py -q`  
Expected: 1 PASS。  
Run: `.venv/bin/ruff check .`  
Expected: `All checks passed!`。  
Run: `DATABASE_URL=sqlite://:memory: .venv/bin/python manage.py check`  
Expected: no issues。

- [ ] **Step 6: 运行完整前端验证**

Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm test`  
Expected: all Vitest suites PASS。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run type-check`  
Expected: PASS with no TypeScript errors。  
Run: `PATH=/opt/homebrew/opt/node@24/bin:$PATH npm run build`  
Expected: PASS and production assets generated in ignored `dist/`。

- [ ] **Step 7: 检查敏感值与变更边界**

Run: `rg -n "04A1B2C3|device_secret|activation_code|TravelWeave-Demo-2026" admin-web/src`  
Expected: no raw card UID; only type/property names for one-time fields; demo password appears only in login test fixtures, never in production component defaults。  
Run: `git diff --check`  
Expected: no whitespace errors。  
Run: `git status --short`  
Expected: only intended source, test and documentation changes before commit。

- [ ] **Step 8: 提交联调与文档切片**

```bash
git add admin-web README.md docs/superpowers/specs/2026-07-22-admin-web-v1-design.md
git commit -m "feat(admin-web): complete management demo flow"
```

## Final Acceptance Walkthrough

- [ ] Run `python manage.py seed_jiang_an_demo` in the configured development backend and confirm it prints success without duplicating data.
- [ ] Login as `demo_admin` and confirm environment, Scene and permissions are visible.
- [ ] Confirm dashboard modules display real API data and independent failure states.
- [ ] Edit a Spot, create a Device, rotate its secret once, import a Card, generate one activation code, force-unbind one test binding, and locate every operation in Audit Logs.
- [ ] Confirm no normal list or detail exposes full UID, stored activation code, stored device secret or JWT.
- [ ] Confirm Photos/AI is visibly marked “规划中” and cannot be navigated to.
- [ ] Confirm the working tree is clean after the final commit and do not merge into `master`.
