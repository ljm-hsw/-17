# 游迹织梦 Demo Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建成 Django + DRF 的基础数据与 API 后端，跑通多卡绑定、ESP32 真实打卡、小程序个人数据和 Web 管理端查询闭环，并为未来 Agent 提供可复用的受控查询服务。

**Architecture:** 继续采用现有 Django 模块化单体。`accounts` 管理微信用户、卡片与绑定，`scenes` 管理场景、点位和推荐路线，`iot` 管理设备身份，`visits` 管理事件、自然日会话与查询；各端只通过 `/api/v1/` 访问这些领域服务。HTTP View 不直接拼接跨领域规则，未来 Agent 工具复用相同 selector/service。

**Tech Stack:** Python 3.12、Django 5.2 LTS、Django REST Framework 3.16、PostgreSQL、Simple JWT 5.5、cryptography 49、drf-spectacular、pytest-django、Ruff。

依赖版本已按官方包页面核对：[djangorestframework-simplejwt 5.5.1](https://pypi.org/project/djangorestframework-simplejwt/) 支持 Django 5.2 与 Python 3.12，[cryptography 49.0.0](https://pypi.org/project/cryptography/) 支持 Python 3.12。

## Global Constraints

- 只在 `test` 分支及其短生命周期功能分支工作，不合并到 `master`。
- 后端是业务事实唯一来源；小程序、管理端、设备和未来 Agent 不直接访问数据库。
- API 固定使用 `/api/v1/`、JSON、`snake_case` 和稳定错误码。
- 一个用户可同时绑定多张有效卡；一张卡同一时刻只属于一个用户；一个用户最多一张主要卡。
- 手机 NFC 绑定不消费激活码；手输 UID 必须消费匹配的一次性激活码。
- 同一用户不同卡在同一 Scene、同一当地自然日汇总到同一个 `VisitSession`。
- `(device, event_id)` 保证设备事件幂等；只有 `accepted` 事件进入进度和路线。
- 完整卡 UID、激活码、设备密钥、微信密钥和 JWT 不进入普通响应或日志。
- 数据库迁移和初始化命令必须进入版本控制；不手工改表。
- 每个任务遵循测试先行、Ruff 检查和独立 Conventional Commit。
- 设计依据：`docs/superpowers/specs/2026-07-21-base-data-api-design.md`。

## File Structure

```text
backend/
├── apps/
│   ├── common/
│   │   ├── api.py                 # 成功响应和分页封装
│   │   ├── errors.py              # 稳定业务异常和 DRF 异常处理
│   │   ├── middleware.py          # request_id
│   │   ├── models.py              # AuditLog
│   │   ├── audit.py               # 审计写入服务
│   │   ├── permissions.py         # 管理端角色与模型权限
│   │   └── management_urls.py     # 汇总各领域管理路由
│   ├── accounts/
│   │   ├── models.py              # User、Card、CardActivationCode、CardBinding
│   │   ├── uid.py                 # UID 标准化、HMAC、脱敏
│   │   ├── wechat.py              # 微信 code 交换
│   │   ├── services.py            # 绑卡、解绑、主要卡事务
│   │   ├── selectors.py           # 当前用户卡片查询
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── management_views.py
│   ├── scenes/
│   │   ├── models.py              # Scene、Spot、SpotMedia、Route、RouteSpot
│   │   ├── selectors.py           # 已发布场景/点位/路线查询
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── management_views.py
│   ├── iot/
│   │   ├── models.py              # Device、DeviceRequestNonce
│   │   ├── crypto.py              # 设备密钥加解密
│   │   ├── authentication.py      # HMAC 校验、时间窗和 Nonce
│   │   ├── serializers.py
│   │   ├── views.py               # 心跳和打卡入口
│   │   ├── urls.py
│   │   └── management_views.py
│   └── visits/
│       ├── models.py              # VisitSession、CheckinEvent
│       ├── services.py            # 幂等打卡事务
│       ├── selectors.py           # 进度、路线、首页和筛选查询
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── management_views.py
├── tests/
│   ├── factories.py               # 无第三方 factory 依赖的测试对象构造器
│   ├── conftest.py                # APIClient、用户、卡片、设备等共享 fixture
│   ├── test_api_contract.py
│   ├── test_scene_api.py
│   ├── test_card_models.py
│   ├── test_card_binding_api.py
│   ├── test_device_authentication.py
│   ├── test_checkin_api.py
│   ├── test_visit_api.py
│   ├── test_management_api.py
│   └── test_demo_flow.py
└── config/
    ├── settings/base.py
    └── urls.py
```

---

### Task 1: Establish the API Contract and Authentication Foundation

**Files:**
- Modify: `backend/requirements/base.txt`
- Modify: `backend/config/settings/base.py`
- Modify: `backend/config/settings/test.py`
- Modify: `backend/config/settings/production.py`
- Modify: `backend/config/urls.py`
- Modify: `backend/.env.example`
- Create: `backend/apps/common/api.py`
- Create: `backend/apps/common/errors.py`
- Create: `backend/apps/common/middleware.py`
- Modify: `backend/apps/common/views.py`
- Create: `backend/tests/test_api_contract.py`
- Modify: `backend/tests/test_health.py`

**Interfaces:**
- Consumes: Existing `HealthView` and `/api/v1/health`.
- Produces: `api_response(request, data, status_code=200)`, `ApiError(code, message, status_code, details=None)`, `api_exception_handler(exc, context)`, request attribute `request.request_id`, JWT authentication defaults.

- [ ] **Step 1: Add failing envelope and request ID tests**

```python
# backend/tests/test_api_contract.py
from django.urls import reverse


def test_every_success_response_contains_request_id(client):
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok"}
    assert response.json()["request_id"]
    assert response.headers["X-Request-ID"] == response.json()["request_id"]


def test_unknown_api_path_uses_stable_error_envelope(client):
    response = client.get("/api/v1/not-found")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert response.json()["request_id"]
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_api_contract.py tests/test_health.py -q`

Expected: FAIL because responses do not contain `request_id` and the 404 is not wrapped.

- [ ] **Step 3: Add exact runtime dependencies and settings**

Append to `backend/requirements/base.txt`:

```text
djangorestframework-simplejwt~=5.5.0
cryptography~=49.0.0
```

Add to `REST_FRAMEWORK`:

```python
"DEFAULT_AUTHENTICATION_CLASSES": (
    "rest_framework_simplejwt.authentication.JWTAuthentication",
),
"EXCEPTION_HANDLER": "apps.common.errors.api_exception_handler",
```

Add `apps.common.middleware.RequestIdMiddleware` after `SecurityMiddleware`. Add these environment settings:

```python
CARD_UID_HMAC_KEY = env("CARD_UID_HMAC_KEY", default="unsafe-test-card-key")
DEVICE_SECRET_ENCRYPTION_KEY = env("DEVICE_SECRET_ENCRYPTION_KEY", default="")
DEVICE_SIGNATURE_MAX_AGE_SECONDS = env.int("DEVICE_SIGNATURE_MAX_AGE_SECONDS", default=300)
WECHAT_APP_ID = env("WECHAT_APP_ID", default="")
WECHAT_APP_SECRET = env("WECHAT_APP_SECRET", default="")
```

Add matching variable names to `.env.example`; use descriptive replacement strings, never real credentials.

Set a deterministic valid Fernet key only in `settings/test.py`:

```python
DEVICE_SECRET_ENCRYPTION_KEY = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
CARD_UID_HMAC_KEY = "test-card-hmac-key"
```

In `settings/production.py`, read both security keys without defaults so startup fails when either is missing.

- [ ] **Step 4: Implement the shared API helpers**

```python
# backend/apps/common/api.py
from rest_framework.response import Response


def api_response(request, data, status_code=200, meta=None):
    payload = {"data": data}
    if meta is not None:
        payload["meta"] = meta
    payload["request_id"] = request.request_id
    return Response(payload, status=status_code)
```

```python
# backend/apps/common/middleware.py
import uuid


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex}"
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response
```

`api_exception_handler` must map DRF 400/401/403/404/409/429/500 to `VALIDATION_ERROR`、`AUTH_REQUIRED`、`PERMISSION_DENIED`、`RESOURCE_NOT_FOUND`、`CONFLICT`、`RATE_LIMITED`、`SERVICE_UNAVAILABLE` and include `request_id`. Add a JSON `handler404` in `config.urls` so unmatched `/api/` paths use the same envelope. Update `HealthView` to call `api_response`.

- [ ] **Step 5: Install dependencies and run verification**

Run:

```bash
cd backend
.venv/bin/pip install -r requirements/dev.txt
.venv/bin/python -m pytest tests/test_api_contract.py tests/test_health.py -q
.venv/bin/ruff check apps tests
```

Expected: focused tests PASS and Ruff reports no errors.

- [ ] **Step 6: Commit**

```bash
git add backend
git commit -m "feat(api): establish response and auth foundation"
```

---

### Task 2: Add Scene, Spot, Media, and Route Data

**Files:**
- Modify: `backend/apps/scenes/models.py`
- Create: `backend/apps/scenes/migrations/0001_initial.py`
- Create: `backend/apps/scenes/selectors.py`
- Create: `backend/apps/scenes/serializers.py`
- Create: `backend/apps/scenes/views.py`
- Create: `backend/apps/scenes/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/factories.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_scene_api.py`

**Interfaces:**
- Consumes: `api_response` from Task 1.
- Produces: `Scene`, `Spot`, `SpotMedia`, `Route`, `RouteSpot`; `get_published_scene(slug)`, `list_published_spots(scene, category=None)`; public scene/spot/route endpoints.

- [ ] **Step 1: Write failing model and public API tests**

```python
def test_scene_spot_and_route_constraints(db, scene, spots):
    route = Route.objects.create(
        scene=scene,
        slug="classic",
        name="江安经典路线",
        estimated_minutes=150,
        status=Route.Status.PUBLISHED,
    )
    RouteSpot.objects.create(route=route, spot=spots[0], order=1)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            RouteSpot.objects.create(route=route, spot=spots[0], order=2)


def test_spot_list_returns_only_published_spots(api_client, scene, spots):
    response = api_client.get(f"/api/v1/scenes/{scene.slug}/spots")
    assert response.status_code == 200
    assert [item["name"] for item in response.json()["data"]["items"]] == [spots[0].name]
```

`tests/factories.py` must provide plain helper functions `make_user`, `make_scene`, and `make_spot`; later tasks extend it with `make_card` and `make_device`. Do not introduce Factory Boy. Start `tests/conftest.py` with:

```python
import pytest
from rest_framework.test import APIClient

from tests.factories import make_scene, make_spot, make_user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return make_user(username="visitor")


@pytest.fixture
def scene(db):
    return make_scene(slug="jiang-an-campus")


@pytest.fixture
def spots(scene):
    return [
        make_spot(scene=scene, slug="library", status="published"),
        make_spot(scene=scene, slug="draft-spot", status="draft"),
    ]
```

- [ ] **Step 2: Run tests and verify model import failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_scene_api.py -q`

Expected: FAIL because `Scene`, `Spot`, `Route`, and `RouteSpot` are undefined.

- [ ] **Step 3: Implement models and migration**

Implement UUID primary keys and the fields from spec section 4.5–4.8. Use these stable enums and constraints:

```python
class PublishStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    PUBLISHED = "published", "已发布"
    DISABLED = "disabled", "已停用"


class SpotCategory(models.TextChoices):
    LANDMARK = "landmark", "标志景观"
    CHECKIN = "checkin", "普通打卡点"
    PHOTO = "photo", "拍照打卡点"
    STUDY = "study", "学习空间"
    SERVICE = "service", "生活服务"
```

Add `UniqueConstraint(fields=("scene", "slug"), name="uniq_spot_slug_per_scene")`, coordinate checks for `0 <= map_x <= 1` and `0 <= map_y <= 1`, and route-stop uniqueness on `(route, order)` and `(route, spot)`.

- [ ] **Step 4: Implement public selectors and read-only APIs**

Implement:

```python
def get_published_scene(slug: str) -> Scene:
    return Scene.objects.get(slug=slug, status=PublishStatus.PUBLISHED)


def list_published_spots(scene: Scene, category: str | None = None):
    queryset = scene.spots.filter(status=PublishStatus.PUBLISHED).prefetch_related("media")
    return queryset.filter(category=category) if category else queryset
```

Expose:

```text
GET /api/v1/scenes/{scene_slug}
GET /api/v1/scenes/{scene_slug}/spots
GET /api/v1/spots/{spot_id}
GET /api/v1/spots/{spot_id}/related
GET /api/v1/scenes/{scene_slug}/routes
GET /api/v1/routes/{route_id}
```

Anonymous callers receive only published public content; authenticated personal check-in status is added in Task 7.

- [ ] **Step 5: Create and verify migration and APIs**

Run:

```bash
cd backend
.venv/bin/python manage.py makemigrations scenes
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest tests/test_scene_api.py -q
.venv/bin/ruff check apps/scenes tests/test_scene_api.py tests/factories.py
```

Expected: migration applies, tests PASS, Ruff clean.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/scenes backend/tests backend/config/urls.py
git commit -m "feat(scenes): add spots and recommended routes"
```

---

### Task 3: Add Multi-Card Domain Models and UID Protection

**Files:**
- Modify: `backend/apps/accounts/models.py`
- Create: `backend/apps/accounts/uid.py`
- Create: `backend/apps/accounts/migrations/0002_user_profile_cards_and_bindings.py`
- Modify: `backend/apps/accounts/admin.py`
- Modify: `backend/tests/conftest.py`
- Create: `backend/tests/test_card_models.py`

**Interfaces:**
- Consumes: `settings.CARD_UID_HMAC_KEY`.
- Produces: `normalize_card_uid(raw) -> str`, `digest_card_uid(raw) -> str`, `mask_card_uid(raw) -> str`; `Card`, `CardActivationCode`, `CardBinding` and their constraints.

- [ ] **Step 1: Write failing UID and constraint tests**

```python
def test_uid_helpers_are_stable_and_do_not_return_plain_uid(settings):
    settings.CARD_UID_HMAC_KEY = "test-hmac-key"
    assert normalize_card_uid("04:a1-b2 c3") == "04A1B2C3"
    assert digest_card_uid("04:a1-b2 c3") == digest_card_uid("04A1B2C3")
    assert digest_card_uid("04A1B2C3") != "04A1B2C3"
    assert mask_card_uid("04A1B2C3") == "****B2C3"


def test_user_can_have_multiple_active_cards_but_card_has_one_owner(db, user, cards):
    CardBinding.objects.create(user=user, card=cards[0], is_primary=True)
    CardBinding.objects.create(user=user, card=cards[1], is_primary=False)
    assert CardBinding.objects.filter(user=user, unbound_at__isnull=True).count() == 2
```

Add separate tests that two active owners for one card and two active primary cards for one user raise `IntegrityError` inside `transaction.atomic()`.

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_card_models.py -q`

Expected: FAIL because UID helpers and card models do not exist.

- [ ] **Step 3: Implement UID helpers**

```python
import hashlib
import hmac
import re

from django.conf import settings


def normalize_card_uid(raw: str) -> str:
    value = re.sub(r"[^0-9A-Fa-f]", "", raw).upper()
    if not 8 <= len(value) <= 32 or len(value) % 2:
        raise ValueError("invalid_card_uid")
    return value


def digest_card_uid(raw: str) -> str:
    value = normalize_card_uid(raw)
    return hmac.new(
        settings.CARD_UID_HMAC_KEY.encode(), value.encode(), hashlib.sha256
    ).hexdigest()


def mask_card_uid(raw: str) -> str:
    return f"****{normalize_card_uid(raw)[-4:]}"
```

- [ ] **Step 4: Implement card models and database constraints**

Add profile fields to `User`, then implement all fields from spec sections 4.2–4.4. The two partial constraints must be exactly:

```python
models.UniqueConstraint(
    fields=("card",),
    condition=models.Q(unbound_at__isnull=True),
    name="uniq_active_binding_per_card",
)
models.UniqueConstraint(
    fields=("user",),
    condition=models.Q(unbound_at__isnull=True, is_primary=True),
    name="uniq_primary_binding_per_user",
)
```

Store activation codes with `make_password`/`check_password`. Never add a plaintext activation-code column.

Extend `tests/factories.py` so `make_card(raw_uid, serial_no)` stores only the digest/masked UID and attaches `plain_uid` to the returned in-memory object for test requests. Extend `tests/conftest.py` with a two-card fixture using distinct UIDs.

- [ ] **Step 5: Generate migration and verify**

Run:

```bash
cd backend
.venv/bin/python manage.py makemigrations accounts --name user_profile_cards_and_bindings
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest tests/test_card_models.py tests/test_user_model.py -q
.venv/bin/ruff check apps/accounts tests/test_card_models.py
```

Expected: all focused tests PASS and Ruff clean.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/accounts backend/tests/test_card_models.py
git commit -m "feat(accounts): add secure multi-card models"
```

---

### Task 4: Implement Login and Multi-Card Binding APIs

**Files:**
- Create: `backend/apps/accounts/wechat.py`
- Create: `backend/apps/accounts/services.py`
- Create: `backend/apps/accounts/selectors.py`
- Create: `backend/apps/accounts/serializers.py`
- Create: `backend/apps/accounts/views.py`
- Create: `backend/apps/accounts/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_card_binding_api.py`
- Modify: `backend/tests/conftest.py`

**Interfaces:**
- Consumes: card models and UID helpers from Task 3, Simple JWT from Task 1.
- Produces: `bind_card(*, user, card_uid, bind_method, activation_code=None, alias="") -> CardBinding`, `set_primary_binding(*, user, binding)`, `unbind_card(*, user, binding, reason)`; auth, `/me`, and `/me/cards` endpoints.

- [ ] **Step 1: Write failing binding service and API tests**

Cover these exact cases:

```python
def test_manual_binding_consumes_code_and_allows_second_card(auth_client, cards, codes):
    first = auth_client.post("/api/v1/me/cards/bind", {
        "card_uid": cards[0].plain_uid,
        "activation_code": codes[0].plain_code,
        "bind_method": "manual",
        "alias": "绿色手环",
    }, format="json")
    second = auth_client.post("/api/v1/me/cards/bind", {
        "card_uid": cards[1].plain_uid,
        "activation_code": codes[1].plain_code,
        "bind_method": "manual",
        "alias": "蓝色卡片",
    }, format="json")
    assert first.status_code == second.status_code == 201
    assert CardBinding.objects.filter(user=auth_client.user, unbound_at__isnull=True).count() == 2
    assert CardBinding.objects.filter(user=auth_client.user, is_primary=True).count() == 1
```

Also test NFC binding without a code, invalid/used codes, card owned by another user, setting primary, unbinding a non-primary card, unbinding the primary card, and inability to access another user's binding.

Add this authenticated client fixture before using `auth_client`:

```python
@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    client.user = user
    return client
```

Create each activation code with `make_password`, then attach its one-time plaintext value as `plain_code` only to the in-memory test object.

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_card_binding_api.py -q`

Expected: FAIL because services and routes are missing.

- [ ] **Step 3: Implement transactional binding services**

`bind_card` must be decorated with `transaction.atomic`, lock Card and matching unused activation-code rows with `select_for_update`, reject an active binding, consume a code only for `manual`, and set `is_primary=True` only when the user has no active primary card. Translate integrity conflicts to `ApiError("CARD_ALREADY_BOUND", ..., 409)`.

`unbind_card` must set `unbound_at`, clear primary state, and if necessary promote the most recently bound remaining active binding in the same transaction. Historical rows are never deleted.

- [ ] **Step 4: Implement login and card endpoints**

Expose:

```text
POST /api/v1/auth/wechat/login
POST /api/v1/auth/refresh
POST /api/v1/auth/dev-login
GET  /api/v1/me
PATCH /api/v1/me
GET  /api/v1/me/cards
POST /api/v1/me/cards/bind
PATCH /api/v1/me/cards/{binding_id}
POST /api/v1/me/cards/{binding_id}/set-primary
DELETE /api/v1/me/cards/{binding_id}
```

`WechatClient.exchange_code(code)` must call `https://api.weixin.qq.com/sns/jscode2session` with configured app ID/secret, require `openid`, and never log the code or returned session key. `DevLoginView` must return 404 unless `settings.DEBUG` is true. Both login paths issue Simple JWT access and refresh tokens through one helper.

- [ ] **Step 5: Verify binding APIs**

Run:

```bash
cd backend
.venv/bin/python -m pytest tests/test_card_binding_api.py -q
.venv/bin/ruff check apps/accounts tests/test_card_binding_api.py
```

Expected: all binding and authorization tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/accounts backend/config/urls.py backend/tests/test_card_binding_api.py
git commit -m "feat(accounts): add login and multi-card binding APIs"
```

---

### Task 5: Add Device Identity, Secret Protection, and Heartbeat

**Files:**
- Modify: `backend/apps/iot/models.py`
- Create: `backend/apps/iot/migrations/0001_initial.py`
- Create: `backend/apps/iot/crypto.py`
- Create: `backend/apps/iot/authentication.py`
- Create: `backend/apps/iot/serializers.py`
- Create: `backend/apps/iot/views.py`
- Create: `backend/apps/iot/urls.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_device_authentication.py`
- Modify: `backend/tests/factories.py`
- Modify: `backend/tests/conftest.py`

**Interfaces:**
- Consumes: `Scene`, `Spot`, encryption settings, `ApiError`.
- Produces: `Device`, `DeviceRequestNonce`, `encrypt_device_secret`, `decrypt_device_secret`, `DeviceHMACAuthentication`, authenticated `request.auth_device`, `/iot/heartbeat`.

- [ ] **Step 1: Write failing signature tests**

```python
def make_signature(secret, method, path, timestamp, nonce, raw_body):
    body_hash = hashlib.sha256(raw_body).hexdigest()
    canonical = "\n".join((method, path, timestamp, nonce, body_hash))
    return hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()


def test_valid_heartbeat_updates_last_seen(device_client, device):
    response = device_client.post_signed(
        "/api/v1/iot/heartbeat",
        {"firmware_version": "1.0.0"},
        device=device,
    )
    assert response.status_code == 200
    device.refresh_from_db()
    assert device.last_seen_at is not None
```

Add tests for wrong signature, expired timestamp, repeated Nonce, disabled device, and device secret never appearing in API output.

Implement `SignedDeviceClient` in `tests/factories.py` as a small wrapper around DRF `APIClient`: JSON-encode the body once, calculate headers with `make_signature`, then call `client.generic("POST", path, raw_body, content_type="application/json", **headers)`. Add `device` and `device_client` fixtures to `tests/conftest.py` using a known plaintext secret that is encrypted before database storage.

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_device_authentication.py -q`

Expected: FAIL because device authentication does not exist.

- [ ] **Step 3: Implement Device models and secret encryption**

Implement fields from spec section 4.9. `DeviceRequestNonce` contains `device`, `nonce`, `created_at`, `expires_at` and has unique `(device, nonce)`. Use `cryptography.fernet.Fernet` with `DEVICE_SECRET_ENCRYPTION_KEY`:

```python
def encrypt_device_secret(secret: str) -> str:
    return Fernet(settings.DEVICE_SECRET_ENCRYPTION_KEY.encode()).encrypt(secret.encode()).decode()


def decrypt_device_secret(ciphertext: str) -> str:
    return Fernet(settings.DEVICE_SECRET_ENCRYPTION_KEY.encode()).decrypt(ciphertext.encode()).decode()
```

Production settings must reject an empty encryption key.

- [ ] **Step 4: Implement HMAC authentication and heartbeat**

`DeviceHMACAuthentication` must read `X-Device-Id`, `X-Timestamp`, `X-Nonce`, `X-Signature`, enforce the configured 300-second window, calculate the exact canonical string from raw request bytes, compare with `hmac.compare_digest`, then atomically insert the Nonce. It returns `(AnonymousUser(), device)` and sets `request.auth_device` in the view.

Heartbeat accepts only `firmware_version` and a bounded diagnostic `last_error_code`, updates `last_seen_at`, and returns device/spot IDs plus `feedback_code="HEARTBEAT_ACCEPTED"`.

- [ ] **Step 5: Generate migration and verify**

Run:

```bash
cd backend
.venv/bin/python manage.py makemigrations iot
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest tests/test_device_authentication.py -q
.venv/bin/ruff check apps/iot tests/test_device_authentication.py
```

Expected: authentication tests PASS and Ruff clean.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/iot backend/config/urls.py backend/tests/test_device_authentication.py
git commit -m "feat(iot): authenticate devices and accept heartbeats"
```

---

### Task 6: Implement Idempotent Check-In Processing

**Files:**
- Modify: `backend/apps/visits/models.py`
- Create: `backend/apps/visits/migrations/0001_initial.py`
- Create: `backend/apps/visits/services.py`
- Modify: `backend/apps/iot/serializers.py`
- Modify: `backend/apps/iot/views.py`
- Modify: `backend/apps/iot/urls.py`
- Create: `backend/tests/test_checkin_api.py`
- Modify: `backend/tests/factories.py`
- Modify: `backend/tests/conftest.py`

**Interfaces:**
- Consumes: `DeviceHMACAuthentication`, `digest_card_uid`, active `CardBinding`, Scene timezone.
- Produces: `VisitSession`, `CheckinEvent`, `process_checkin(*, device, payload) -> CheckinResult`, `POST /api/v1/iot/checkins`.

- [ ] **Step 1: Write failing accepted, rejected, and duplicate tests**

```python
def test_two_cards_for_one_user_share_daily_session(device_client, device, user, bound_cards):
    first = device_client.post_checkin(device=device, card=bound_cards[0], event_id="event-a")
    second = device_client.post_checkin(device=device, card=bound_cards[1], event_id="event-b")
    assert first.status_code == second.status_code == 200
    assert VisitSession.objects.filter(user=user, scene=device.scene).count() == 1
    assert CheckinEvent.objects.filter(user=user, status="accepted").count() == 2


def test_repeating_device_event_returns_original_result(device_client, device, bound_cards):
    first = device_client.post_checkin(device=device, card=bound_cards[0], event_id="same-event")
    second = device_client.post_checkin(device=device, card=bound_cards[0], event_id="same-event")
    assert second.json()["data"] == first.json()["data"]
    assert CheckinEvent.objects.filter(device=device, event_id="same-event").count() == 1
```

Also test unregistered UID, unbound card, disabled card, Spot mismatch, next-day session creation, and device time not controlling `local_date`.

Extend `SignedDeviceClient` with `post_checkin(device, card, event_id, spot=None, device_time=None)`. Add `bound_cards` fixture that binds both test cards to the same user, making only the first binding primary.

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_checkin_api.py -q`

Expected: FAIL because visit models and check-in service are missing.

- [ ] **Step 3: Implement visit models and constraints**

Implement all fields from spec sections 4.10–4.11. Add:

```python
models.UniqueConstraint(
    fields=("user", "scene", "local_date"),
    name="uniq_daily_visit_per_user_scene",
)
models.UniqueConstraint(
    fields=("device", "event_id"),
    name="uniq_event_id_per_device",
)
```

Add the five query indexes specified in the design. Use `on_delete=PROTECT` for card, binding, device, Spot and Session references so history cannot disappear.

- [ ] **Step 4: Implement the transaction service**

`process_checkin` must execute this exact order inside `transaction.atomic`:

```text
lock/find (device, event_id)
→ return result_snapshot if present
→ validate device Spot
→ digest UID and find Card
→ find active CardBinding
→ reject if Card/binding invalid
→ compute Scene local_date from server now
→ get_or_create VisitSession(user, scene, local_date)
→ create accepted CheckinEvent
→ update session.last_checkin_at and card.last_used_at
→ save result_snapshot
```

For authenticated business failures, create a rejected event with a stable `failure_code` and no `VisitSession`. Catch concurrent unique conflicts by loading and returning the winning event.

- [ ] **Step 5: Expose device check-in endpoint and verify**

The view validates `event_id`, `spot_id`, `card_uid`, `checkin_type`, and optional `device_time`, calls `process_checkin`, then returns status 200 for accepted/duplicate and a stable device feedback payload for rejected business events. It never returns user identity.

Run:

```bash
cd backend
.venv/bin/python manage.py makemigrations visits
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest tests/test_checkin_api.py -q
.venv/bin/ruff check apps/visits apps/iot tests/test_checkin_api.py
```

Expected: all check-in tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/visits backend/apps/iot backend/tests/test_checkin_api.py
git commit -m "feat(visits): process idempotent device check-ins"
```

---

### Task 7: Add Personal Home, Visit, Progress, and Card History APIs

**Files:**
- Create: `backend/apps/visits/selectors.py`
- Create: `backend/apps/visits/serializers.py`
- Create: `backend/apps/visits/views.py`
- Create: `backend/apps/visits/urls.py`
- Modify: `backend/apps/accounts/views.py`
- Modify: `backend/apps/accounts/urls.py`
- Modify: `backend/apps/scenes/serializers.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_visit_api.py`
- Modify: `backend/tests/conftest.py`

**Interfaces:**
- Consumes: accepted `CheckinEvent`, active card bindings, published Spots.
- Produces: `get_current_visit(user, scene, on_date=None)`, `get_checkin_progress(user, session)`, `get_route_timeline(user, session)`, `list_user_checkins(user, filters)` and personal endpoints used later by Agent.

- [ ] **Step 1: Write failing personal-query tests**

```python
def test_today_visit_aggregates_cards_and_deduplicates_spots(auth_client, visit_events, scene):
    response = auth_client.get(f"/api/v1/me/visits/today?scene={scene.slug}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["checked_spot_count"] == 2
    assert data["event_count"] == 3
    assert [item["spot_id"] for item in data["route"]] == visit_events.first_spot_order


def test_card_history_is_scoped_to_current_user(auth_client, other_users_card):
    response = auth_client.get(f"/api/v1/me/cards/{other_users_card.id}/checkins")
    assert response.status_code == 404
```

Also test no-event today response, historical ownership, rejected events excluded, Spot personal status, pagination and filters by card/date/Spot.

Define `visit_events` in `tests/conftest.py` as a fixture that creates three accepted events for the authenticated user: first card at Spot A, second card at Spot B, then first card at Spot A again. Attach `first_spot_order = [str(spot_a.id), str(spot_b.id)]` to the returned list wrapper. Define `other_users_card` as an actively bound card owned by a different user.

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_visit_api.py -q`

Expected: FAIL because selectors and routes are missing.

- [ ] **Step 3: Implement reusable selectors**

Use one accepted-event base queryset:

```python
def accepted_events_for_user(user):
    return (
        CheckinEvent.objects.filter(user=user, status=CheckinEvent.Status.ACCEPTED)
        .select_related("card", "spot", "device", "visit_session")
        .order_by("received_at", "id")
    )
```

`get_route_timeline` must return the first event per Spot in stable chronological order. `get_checkin_progress` uses distinct Spot IDs and the number of published, check-in-enabled Spots in the same Scene. All selector signatures receive a trusted `user` object, never a caller-supplied unrestricted user ID.

- [ ] **Step 4: Implement endpoints**

Expose:

```text
GET /api/v1/me/home?scene={slug}
GET /api/v1/me/visits/today?scene={slug}
GET /api/v1/me/visits/history
GET /api/v1/me/visits/{visit_id}
GET /api/v1/me/checkins
GET /api/v1/me/cards/{card_id}/checkins
```

Add `is_checked_in`, `first_checked_in_at`, and `distance_basis` to authenticated Spot responses. `/me/home` returns Scene summary, primary card, active card count, visit progress, latest accepted event, and up to four published unvisited Spots.

- [ ] **Step 5: Verify personal APIs**

Run:

```bash
cd backend
.venv/bin/python -m pytest tests/test_visit_api.py tests/test_scene_api.py -q
.venv/bin/ruff check apps/visits apps/accounts apps/scenes tests/test_visit_api.py
```

Expected: personal API tests PASS and no cross-user data leaks.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/visits backend/apps/accounts backend/apps/scenes backend/config/urls.py backend/tests/test_visit_api.py
git commit -m "feat(visits): expose personal progress and route APIs"
```

---

### Task 8: Add Management Dashboard and Read APIs

**Files:**
- Create: `backend/apps/common/management_urls.py`
- Create: `backend/apps/accounts/management_views.py`
- Create: `backend/apps/scenes/management_views.py`
- Create: `backend/apps/iot/management_views.py`
- Create: `backend/apps/visits/management_views.py`
- Modify: `backend/config/urls.py`
- Create: `backend/tests/test_management_api.py`
- Modify: `backend/tests/conftest.py`

**Interfaces:**
- Consumes: domain models and selectors from Tasks 2–7.
- Produces: staff-only dashboard, user, card, Spot, Device, Visit, and Checkin read APIs under `/api/v1/management/`.

- [ ] **Step 1: Write failing permission and query tests**

```python
def test_non_staff_cannot_use_management_api(auth_client):
    response = auth_client.get("/api/v1/management/dashboard/summary")
    assert response.status_code == 403


def test_staff_can_trace_same_event_by_user_card_and_spot(staff_client, accepted_event):
    user_events = staff_client.get(
        f"/api/v1/management/users/{accepted_event.user_id}/checkins"
    ).json()["data"]["items"]
    card_events = staff_client.get(
        f"/api/v1/management/cards/{accepted_event.card_id}/checkins"
    ).json()["data"]["items"]
    spot_events = staff_client.get(
        f"/api/v1/management/spots/{accepted_event.spot_id}/checkins"
    ).json()["data"]["items"]
    assert {user_events[0]["id"], card_events[0]["id"], spot_events[0]["id"]} == {
        str(accepted_event.id)
    }
```

Also test date/Scene/status filters, card UID masking, no `wechat_openid`, today visitor distinct count, and Spot visitor count versus event count.

Add `staff_client` in `tests/conftest.py` by creating `is_staff=True` user, calling `force_authenticate`, and attaching it as `client.user`. Add `accepted_event` using the same service as the device endpoint so management tests inspect a realistic event.

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_management_api.py -q`

Expected: FAIL because management routes do not exist.

- [ ] **Step 3: Implement management routers and serializers**

Use DRF read-only ViewSets with `IsAdminUser`. Register exact resources:

```text
dashboard/summary
dashboard/checkin-trend
dashboard/spot-ranking
dashboard/latest-events
dashboard/device-status
users
users/{id}
users/{id}/cards
users/{id}/visits
users/{id}/checkins
scenes
scenes/{id}
spots
spots/{id}
cards
cards/{id}
cards/{id}/bindings
cards/{id}/checkins
spots/{id}/statistics
spots/{id}/checkins
devices
devices/{id}/checkins
routes
routes/{id}
visits
visits/{id}
checkins
checkins/{id}
```

Use query parameters `scene_id`, `date_from`, `date_to`, `status`, `spot_id`, `device_id`, `card_id`, `user_id`. Apply `select_related`/`prefetch_related`; do not issue a query per list row.

- [ ] **Step 4: Implement dashboard calculations**

Define data exactly:

```text
today_visitors = distinct user_id with accepted events in Scene-local date
accepted_checkins = accepted event count in range
bound_cards = active binding count
online_devices = active devices whose last_seen_at is within 120 seconds
spot_visitors = distinct accepted user_id per Spot
spot_events = accepted event count per Spot
```

Return `generated_at`, `scene_id`, and requested range so the UI can label data correctly.

- [ ] **Step 5: Verify management read APIs**

Run:

```bash
cd backend
.venv/bin/python -m pytest tests/test_management_api.py -q
.venv/bin/ruff check apps tests/test_management_api.py
```

Expected: read APIs PASS, non-staff is rejected, sensitive fields absent.

- [ ] **Step 6: Commit**

```bash
git add backend/apps backend/config/urls.py backend/tests/test_management_api.py
git commit -m "feat(management): add dashboard and traceability APIs"
```

---

### Task 9: Add Audited Management Mutations

**Files:**
- Create: `backend/apps/common/models.py`
- Create: `backend/apps/common/migrations/0001_initial.py`
- Create: `backend/apps/common/audit.py`
- Create: `backend/apps/common/permissions.py`
- Modify: `backend/apps/accounts/management_views.py`
- Modify: `backend/apps/scenes/management_views.py`
- Modify: `backend/apps/iot/management_views.py`
- Modify: `backend/apps/common/management_urls.py`
- Modify: `backend/tests/test_management_api.py`

**Interfaces:**
- Consumes: staff authentication and domain models.
- Produces: immutable `AuditLog`, `record_audit(...)`, point/route/card/device write APIs, activation-code generation and device-secret rotation.

- [ ] **Step 1: Add failing mutation and audit tests**

```python
def test_force_unbind_requires_reason_and_writes_audit(staff_client, binding):
    rejected = staff_client.post(
        f"/api/v1/management/bindings/{binding.id}/force-unbind", {}, format="json"
    )
    assert rejected.status_code == 400

    accepted = staff_client.post(
        f"/api/v1/management/bindings/{binding.id}/force-unbind",
        {"reason": "用户报告卡片遗失", "confirm": True},
        format="json",
    )
    assert accepted.status_code == 200
    assert AuditLog.objects.filter(
        actor=staff_client.user,
        action="binding.force_unbind",
        target_id=str(binding.id),
    ).exists()
```

Also test Spot disable instead of delete, Spot media create/reorder/disable, activation-code plaintext shown once, card import preview without writes, confirmed import with per-row results, device secret shown once on create/rotate, route-stop validation, role-restricted writes, and audit endpoint read-only behavior.

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_management_api.py -q`

Expected: new mutation tests FAIL because AuditLog and writes are absent.

- [ ] **Step 3: Implement immutable audit model and service**

`AuditLog` fields are UUID `id`, `actor`, `actor_role`, `action`, `target_type`, `target_id`, JSON `before`, JSON `after`, `reason`, `request_id`, and `created_at`. Do not provide update/delete API methods.

```python
def record_audit(*, request, action, target, before, after, reason):
    return AuditLog.objects.create(
        actor=request.user,
        actor_role="system_admin" if request.user.is_superuser else "staff",
        action=action,
        target_type=target._meta.label_lower,
        target_id=str(target.pk),
        before=before,
        after=after,
        reason=reason,
        request_id=request.request_id,
    )
```

Call it inside the same `transaction.atomic` block as each sensitive mutation.

Create `HasManagementModelPermission` in `common/permissions.py`. It first requires `is_staff`, then maps each HTTP/action pair to Django permissions. Content operators receive Scene/Spot/SpotMedia/Route permissions, device operators receive Device permissions, data administrators receive Card/CardBinding permissions, and superusers retain all permissions. Read endpoints remain available to authenticated staff but continue returning masked serializers.

- [ ] **Step 4: Implement scoped management writes**

Expose:

```text
POST /management/scenes
PATCH /management/scenes/{id}
POST /management/spots
PATCH /management/spots/{id}
POST /management/spots/{id}/publish
POST /management/spots/{id}/disable
POST /management/spots/{id}/media
PATCH /management/spots/{id}/media/{media_id}
POST /management/spots/{id}/media/{media_id}/disable
POST /management/routes
PATCH /management/routes/{id}
POST /management/cards
PATCH /management/cards/{id}
POST /management/cards/import-preview
POST /management/cards/import-confirm
POST /management/cards/{id}/activation-codes
POST /management/bindings/{id}/force-unbind
POST /management/devices
PATCH /management/devices/{id}
POST /management/devices/{id}/rotate-secret
GET /management/audit-logs
```

Return plaintext activation code/device secret only from the successful create/rotate response. Store only hashes or encrypted ciphertext. Require `confirm=true` and a nonblank reason for force-unbind, disable, and rotate operations.

`import-preview` accepts a bounded JSON array of `{serial_no, card_uid}` rows and returns `valid`, `duplicate`, and `invalid` arrays without writing. `import-confirm` accepts the validated rows plus `confirm=true`, creates each card in one transaction, and returns a per-row result; it never echoes a complete UID. Route writes accept nested `{spot_id, order, note}` stops and replace them atomically only after all Spot/Scene relationships validate.

- [ ] **Step 5: Generate migration and verify**

Run:

```bash
cd backend
.venv/bin/python manage.py makemigrations common
.venv/bin/python manage.py migrate
.venv/bin/python -m pytest tests/test_management_api.py -q
.venv/bin/ruff check apps tests/test_management_api.py
```

Expected: all management mutation and audit tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/common backend/apps/accounts backend/apps/scenes backend/apps/iot backend/tests/test_management_api.py
git commit -m "feat(management): add audited operations"
```

---

### Task 10: Seed the Demo, Publish OpenAPI, and Verify the Full Flow

**Files:**
- Create: `backend/apps/scenes/management/commands/seed_jiang_an_demo.py`
- Create: `backend/apps/scenes/management/__init__.py`
- Create: `backend/apps/scenes/management/commands/__init__.py`
- Create: `backend/tests/test_demo_flow.py`
- Modify: `backend/config/urls.py`
- Modify: `backend/README.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: all previous tasks.
- Produces: idempotent `seed_jiang_an_demo`, OpenAPI schema for all endpoints, one-command Demo setup, end-to-end evidence.

- [ ] **Step 1: Write failing seed and end-to-end tests**

```python
def test_seed_command_is_idempotent(db):
    from django.core.management import call_command

    call_command("seed_jiang_an_demo")
    call_command("seed_jiang_an_demo")
    assert Scene.objects.filter(slug="jiang-an-campus").count() == 1
    assert Spot.objects.filter(scene__slug="jiang-an-campus").count() == 8
    assert Route.objects.filter(scene__slug="jiang-an-campus").count() == 2


def test_demo_flow_joins_two_cards_into_one_user_visit(demo_system):
    demo_system.bind_card("SCU-JA-0001")
    demo_system.bind_card("SCU-JA-0002")
    demo_system.check_in("SCU-JA-0001", "library")
    demo_system.check_in("SCU-JA-0002", "mingyuan-lake")
    home = demo_system.get_home()
    assert home["active_card_count"] == 2
    assert home["visit"]["checked_spot_count"] == 2
    assert VisitSession.objects.filter(user=demo_system.user).count() == 1
```

The flow must additionally assert the same CheckinEvent ID appears in user, card and Spot management queries and duplicate `event_id` does not change counts.

- [ ] **Step 2: Run tests and verify failure**

Run: `cd backend && .venv/bin/python -m pytest tests/test_demo_flow.py -q`

Expected: FAIL because seed command and Demo fixture are missing.

- [ ] **Step 3: Implement idempotent seed command**

Use `update_or_create` for one `jiang-an-campus` Scene, exactly eight reviewed Spot slugs, two Routes with explicit RouteSpot order, one active Demo device and three available test cards. Generate activation codes only when a card has no unused code. Do not hard-code a production device secret; accept `--device-secret` or generate a Demo-only value and print it once to stdout.

Use `Group` and `Permission` to idempotently create `content_operator`, `device_operator`, and `data_administrator` groups with exactly the model permissions defined in Task 9.

The exact eight Spot slugs are:

```text
jiang-an-library
mingyuan-lake
long-bridge
knowledge-square
lakeside-greenway
south-gate
arts-building
sports-center
```

- [ ] **Step 4: Complete schema and runbook documentation**

Ensure these endpoints are available:

```text
GET /api/schema/
GET /api/docs/
```

Document exact commands in `backend/README.md`:

```bash
docker compose --env-file infra/.env.example -f infra/compose.yaml up -d postgres
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements/dev.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_jiang_an_demo
.venv/bin/python manage.py runserver
```

Also document that `/auth/dev-login` is local-only and that the printed activation codes/device secret must not be committed.

- [ ] **Step 5: Run the full backend verification suite**

Run:

```bash
cd backend
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py spectacular --file /tmp/travelweave-openapi.yaml --validate
```

Expected: all tests PASS, Ruff has zero errors, no missing migrations, OpenAPI validation succeeds.

- [ ] **Step 6: Perform one real PostgreSQL smoke run**

Run:

```bash
docker compose --env-file infra/.env.example -f infra/compose.yaml up -d postgres
cd backend
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_jiang_an_demo
.venv/bin/python manage.py check
```

Expected: migrations and seed complete without error; Django system check reports no issues.

- [ ] **Step 7: Commit**

```bash
git add backend README.md
git commit -m "feat(demo): seed and verify backend data flow"
```

---

## Completion Gate

Do not hand the backend to frontend or firmware teammates until all conditions hold:

- Full pytest suite passes against PostgreSQL.
- Ruff lint and format checks pass.
- `makemigrations --check --dry-run` reports no changes.
- OpenAPI schema validates.
- A user binds two cards and both cards contribute to one daily VisitSession.
- Duplicate device event remains one row and one processing result.
- Small-program endpoints never expose another user's data.
- Management endpoints trace one event consistently by user, card, Spot and Device.
- Complete UID, activation code, device secret and WeChat identity are absent from ordinary responses.
- Seed command is idempotent and the full Demo can be reproduced from a clean database.
