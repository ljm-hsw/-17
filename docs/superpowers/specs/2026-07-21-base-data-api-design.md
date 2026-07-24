# 游迹织梦 Demo 基础数据模型与 API 契约

> 文档状态：待团队评审 v0.1
> 适用范围：四川大学江安校区参赛 Demo
> 依赖文档：产品与业务规则、技术架构、Web 管理端设计
> 本文优先级：本文对“一个账号可绑定多张卡”的新决定优先于早期文档中的单卡表述。

## 1. 目标

第一阶段先完成一条可运行、可查询、可展示的四端数据闭环：

```text
微信用户登录
→ 绑定一张或多张 RFID/NFC 卡片
→ ESP32 在真实点位上报刷卡事件
→ Django 校验、去重并保存
→ 小程序展示首页、地图、进度和记录
→ Web 管理端按用户、卡片、点位和设备查询同一批真实数据
```

本阶段不实现复杂 Agent，但数据模型和应用服务必须保证后续 Agent 可以复用受权限控制的路线、进度、点位和推荐查询能力。Agent 不得直接查询数据库。

## 2. Demo 范围

### 2.1 第一阶段必须实现

- 微信正式登录接口及仅开发环境可用的 Demo 登录；
- 一个用户同时绑定多张卡，一张卡同时只属于一个用户；
- 江安校区 Scene、点位、图片和一至两条推荐路线；
- 设备登记、心跳、HMAC 认证和打卡事件幂等接收；
- 按中国标准时间自然日生成用户游览会话；
- 小程序首页、地图、点位详情、打卡记录和绑卡所需接口；
- 管理端看板以及用户、卡片、点位、设备、游览和打卡查询；
- 管理端点位、路线、设备和卡片的基础运营能力；
- 统一响应格式、错误码、权限和自动化测试。

### 2.2 后续扩展，不阻塞第一阶段

- Dify Agent、AI 对话和游记生成；
- 打卡照片和对象存储；
- 收藏、徽章、消息通知；
- 复杂个性化推荐和实时定位；
- 多客户、多租户和微服务。

第一阶段可以保留对应 Django App，不提前创建未经使用的大量字段或空接口。

## 3. 业务规则

### 3.1 用户与卡片

1. 绑定主体是微信账号，不是手机设备。
2. 一个用户可以同时拥有多条有效卡片绑定。
3. 一张卡同一时刻最多存在一条有效绑定。
4. 用户可以在有效卡片中指定一张主要展示卡；最多一张主要卡。
5. 用户第一张有效卡自动成为主要卡。主要卡解绑后，后端自动选择剩余有效卡中最近绑定的一张；没有剩余卡时主要卡为空。
6. 手机 NFC 读取用于证明用户当时接触实体卡；手机不支持或读取失败时，手工输入 UID 必须同时提交实体卡上的一次性激活码。
7. 解绑只结束绑定关系，不删除卡片、打卡、游览或其他历史数据。
8. 卡 UID 是识别符，不是登录凭据。完整 UID 只在绑定或打卡请求处理期间短暂存在；数据库保存服务端 HMAC 和脱敏显示值。

### 3.2 游览与打卡

1. 同一用户、同一 Scene、同一 `Asia/Shanghai` 自然日只有一个 `VisitSession`。
2. 用户当天不同已绑定卡产生的有效事件汇总到同一游览会话。
3. 每条事件仍保存具体卡片和当时的绑定记录，因此可以按卡单独查询。
4. `(device, event_id)` 是设备事件幂等键。重传返回第一次处理结果，不新增事件。
5. 同一用户在同一会话重复打卡同一 Spot，可以保留多个有效事件；完成度和默认路线只计算首次有效到达。
6. 只有 `accepted` 事件进入用户路线、完成度、推荐和未来 Agent 的事实来源。
7. 设备服务端接收时间是会话划分和默认排序依据；`device_time` 只用于展示和排障。
8. 无有效绑定、设备/点位不匹配等经认证请求保存为拒绝事件；签名无效等未通过设备认证的请求只写安全日志。

### 3.3 UI 数据口径

- “卡片在线”不是可验证状态。卡片只能显示已绑定、可用、停用、丢失和最近使用时间；在线状态属于 ESP32 设备。
- 未申请手机定位权限时，不返回“距当前位置”。可以返回“距最近有效打卡点”的预设距离，并明确 `distance_basis=last_checkin_spot`。
- 首页完成度、今日打卡数、最近打卡、点位热度等均从有效事件计算，不在多个表重复保存。

## 4. 数据模型

所有业务主键使用 UUID；时间使用带时区的 UTC 时间保存，展示和 `local_date` 计算使用 Scene 时区。

### 4.1 `accounts.User`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `wechat_openid` | string, nullable | 微信稳定标识，正式用户唯一 |
| `nickname` | string | 展示昵称 |
| `avatar_url` | string | 头像 URL |
| `status` | enum | `active/disabled` |
| `last_login_at` | datetime | 最近登录时间 |
| `created_at`、`updated_at` | datetime | 审计时间 |

开发 Demo 用户必须有明确的 `is_demo` 标记，不能伪造微信 `openid`。

### 4.2 `accounts.Card`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `serial_no` | string | 可展示的卡片/手环编号，例如 `SCU-JA-0001`，唯一 |
| `uid_hmac` | string | 使用服务端密钥计算的 UID HMAC，唯一 |
| `uid_masked` | string | 脱敏值，例如 `****8A3F` |
| `status` | enum | `available/active/lost/disabled` |
| `issued_at` | datetime, nullable | 发放时间 |
| `last_used_at` | datetime, nullable | 最近有效打卡时间 |
| `created_at`、`updated_at` | datetime | 审计时间 |

不保存可直接展示的完整 UID。

### 4.3 `accounts.CardActivationCode`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `card_id` | FK | 所属卡片 |
| `code_hash` | string | 激活码安全散列 |
| `status` | enum | `unused/used/revoked/expired` |
| `expires_at` | datetime, nullable | 过期时间 |
| `used_by_id` | FK, nullable | 使用者 |
| `used_at`、`revoked_at` | datetime, nullable | 状态时间 |
| `created_at` | datetime | 创建时间 |

明文激活码只在生成/导出时显示一次。

### 4.4 `accounts.CardBinding`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `user_id` | FK | 用户 |
| `card_id` | FK | 卡片 |
| `activation_code_id` | FK, nullable | 手输 UID 时使用的激活码；NFC 路径为空 |
| `bind_method` | enum | `nfc/manual/admin` |
| `alias` | string | 用户自定义名称，可空 |
| `is_primary` | boolean | 是否主要展示卡 |
| `bound_at` | datetime | 绑定时间 |
| `unbound_at` | datetime, nullable | 为空表示当前有效 |
| `unbound_reason` | string | 解绑原因，可空 |

数据库约束：

- `card_id WHERE unbound_at IS NULL` 条件唯一；
- `user_id WHERE unbound_at IS NULL AND is_primary = TRUE` 条件唯一；
- 不对用户的有效绑定数量建立唯一约束。

### 4.5 `scenes.Scene`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `slug` | string | 稳定业务标识，唯一 |
| `name`、`subtitle` | string | 展示名称 |
| `timezone` | string | 默认 `Asia/Shanghai` |
| `map_image_url` | string | 地图底图 |
| `status` | enum | `draft/published/disabled` |
| `created_at`、`updated_at` | datetime | 审计时间 |

### 4.6 `scenes.Spot`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `scene_id` | FK | 所属场景 |
| `slug` | string | 场景内稳定标识 |
| `name` | string | 点位名称 |
| `category` | enum | 景观、学习空间、生活服务等 |
| `summary`、`description` | text | 简介和详情 |
| `knowledge_content` | text | 经审核、可供未来 Agent 使用的事实资料 |
| `map_x`、`map_y` | decimal | 0–1 比例坐标 |
| `tags` | JSON array | 标签 |
| `suggested_stay_minutes` | integer | 建议停留时间 |
| `is_checkin_enabled` | boolean | 是否参与打卡 |
| `is_photo_spot` | boolean | 是否拍照点 |
| `status` | enum | `draft/published/disabled` |
| `created_at`、`updated_at` | datetime | 审计时间 |

约束：`(scene_id, slug)` 唯一，地图坐标范围为 0–1。已有历史事件的点位只能停用，不能物理删除。

### 4.7 `scenes.SpotMedia`

保存点位图片 URL/对象键、类型、说明、排序和状态。第一阶段可以使用公开演示图片 URL；以后替换为对象存储不改变点位接口结构。

### 4.8 `scenes.Route` 与 `scenes.RouteSpot`

`Route` 保存 Scene、名称、简介、预计时长、状态；`RouteSpot` 保存路线、点位、顺序和建议说明。`(route, order)` 和 `(route, spot)` 唯一。

第一阶段“加入路线”只表示选择当前推荐路线，不承诺实时导航。若需要跨设备保存用户选择，再增加 `UserRouteSelection`，不阻塞基础打卡链。

### 4.9 `iot.Device`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `device_id` | string | 设备业务标识，唯一 |
| `scene_id`、`spot_id` | FK | 当前归属 |
| `device_type` | enum | `rfid/photo/combined` |
| `secret_encrypted` | binary/text | 受主密钥保护的设备密钥 |
| `secret_fingerprint` | string | 后台展示指纹 |
| `status` | enum | `active/disabled` |
| `firmware_version` | string | 固件版本 |
| `last_seen_at` | datetime | 最近心跳/请求 |
| `last_error_code` | string | 最近错误，可空 |

在线/离线由 `last_seen_at` 与配置阈值计算，不单独作为永久事实。

### 4.10 `visits.VisitSession`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `user_id`、`scene_id` | FK | 用户和场景 |
| `local_date` | date | Scene 当地自然日 |
| `started_at` | datetime | 首次有效打卡时间 |
| `last_checkin_at` | datetime | 最近有效打卡时间 |
| `created_at`、`updated_at` | datetime | 审计时间 |

约束：`(user_id, scene_id, local_date)` 唯一。

### 4.11 `visits.CheckinEvent`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `event_id` | UUID/string | 设备生成的事件 ID |
| `device_id`、`spot_id` | FK | 上报设备与事件点位 |
| `user_id` | FK, nullable | 接受事件对应用户 |
| `card_id` | FK, nullable | 匹配到的卡片 |
| `card_binding_id` | FK, nullable | 事件发生时的绑定 |
| `visit_session_id` | FK, nullable | 接受事件所属游览 |
| `card_uid_hmac` | string | 服务端计算的 UID 摘要 |
| `checkin_type` | enum | `nfc/rfid/manual_admin` |
| `status` | enum | `accepted/rejected` |
| `failure_code` | string | 拒绝原因，可空 |
| `device_time` | datetime, nullable | 设备时间 |
| `received_at` | datetime | 服务端接收时间 |
| `result_snapshot` | JSON | 首次处理后供幂等重放的脱敏结果 |

约束与索引：

- `(device_id, event_id)` 唯一；
- 索引 `(user_id, received_at)`；
- 索引 `(card_id, received_at)`；
- 索引 `(spot_id, received_at)`；
- 索引 `(device_id, received_at)`；
- 索引 `(visit_session_id, status, received_at)`。

### 4.12 `common.AuditLog`

保存管理员、角色、动作、目标类型与 ID、变更前后脱敏摘要、原因、时间和 `request_id`。普通管理端不可修改或删除。

## 5. 统一 API 约定

### 5.1 基础规则

- 前缀：`/api/v1/`；
- 正式环境仅 HTTPS；
- JSON 字段使用 `snake_case`；
- 时间使用 ISO 8601，例如 `2026-07-21T10:45:00+08:00`；
- UUID 对外使用字符串；
- 游客 JWT、管理员 JWT、设备 HMAC 使用独立权限类；
- 小程序接口不得通过传入 `user_id` 查询他人数据；
- 管理接口固定在 `/api/v1/management/`。

成功响应：

```json
{
  "data": {},
  "request_id": "req_01..."
}
```

列表响应：

```json
{
  "data": {"items": []},
  "meta": {"page": 1, "page_size": 20, "total": 0},
  "request_id": "req_01..."
}
```

失败响应：

```json
{
  "error": {
    "code": "CARD_ALREADY_BOUND",
    "message": "该卡片已绑定其他账号",
    "details": {}
  },
  "request_id": "req_01..."
}
```

### 5.2 游客认证与个人资料

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/auth/wechat/login` | 微信临时 code 换取后端访问/刷新令牌 |
| POST | `/auth/refresh` | 轮换访问令牌 |
| POST | `/auth/dev-login` | 仅 `DEBUG`/测试环境创建 Demo 会话 |
| GET | `/me` | 当前用户资料与卡片数量摘要 |
| PATCH | `/me` | 修改允许的展示资料 |
| GET | `/me/home?scene=jiang-an-campus` | 首页聚合数据 |

`GET /me/home` 至少返回：Scene 摘要、主要卡、有效卡数量、当天游览摘要、最近打卡、首页推荐点位。

### 5.3 卡片接口

| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/me/cards` | 当前有效卡和历史绑定 |
| POST | `/me/cards/bind` | 绑定新卡 |
| PATCH | `/me/cards/{binding_id}` | 修改别名 |
| POST | `/me/cards/{binding_id}/set-primary` | 设置主要卡 |
| DELETE | `/me/cards/{binding_id}` | 解绑，需确认参数 |
| GET | `/me/cards/{card_id}/checkins` | 查询本人指定卡的打卡记录 |

绑定请求：

```json
{
  "card_uid": "04A1B2C3D4",
  "bind_method": "nfc",
  "alias": "绿色手环"
}
```

`bind_method=manual` 时必须额外提交 `activation_code`；`bind_method=nfc` 时由受支持的手机 NFC 交互取得 UID，不消费激活码。

响应不得返回完整 UID 或激活码。

### 5.4 场景、点位和路线接口

| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/scenes/{scene_slug}` | 场景和地图资料 |
| GET | `/scenes/{scene_slug}/spots` | 点位列表，可按分类和打卡状态筛选 |
| GET | `/spots/{spot_id}` | 点位详情和当前用户打卡状态 |
| GET | `/spots/{spot_id}/related` | 相关点位 |
| GET | `/scenes/{scene_slug}/routes` | 已发布推荐路线 |
| GET | `/routes/{route_id}` | 路线详情和点位顺序 |

点位响应中的个人状态由后端根据当前用户有效事件计算。匿名浏览可以返回公开资料，但不返回个人打卡信息。

### 5.5 游览和记录接口

| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/me/visits/today?scene=jiang-an-campus` | 当日进度、路线和已/未打卡摘要 |
| GET | `/me/visits/history` | 历史自然日游览分页列表 |
| GET | `/me/visits/{visit_id}` | 指定游览详情，必须验证所有权 |
| GET | `/me/checkins` | 按日期、卡片、点位筛选个人事件 |

当天没有有效打卡时，`today` 返回 `visit: null` 和零进度，不为展示目的创建空会话。

### 5.6 设备接口

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/iot/heartbeat` | 更新设备最近在线时间、固件版本和诊断摘要 |
| POST | `/iot/checkins` | 上报打卡事件 |

设备请求头：

```text
X-Device-Id
X-Timestamp
X-Nonce
X-Signature
```

签名原文：

```text
METHOD + "\n" + PATH + "\n" + TIMESTAMP + "\n" + NONCE + "\n" + SHA256(raw_body)
```

打卡请求：

```json
{
  "event_id": "8c8fbf16-5ed7-4b20-af73-579dd55945ab",
  "spot_id": "8b5c...",
  "card_uid": "04A1B2C3D4",
  "checkin_type": "nfc",
  "device_time": "2026-07-21T10:45:00+08:00"
}
```

成功或幂等重复响应只返回事件结果、点位摘要和反馈码，不返回用户昵称、微信身份或完整卡 UID。

### 5.7 管理端接口

#### 看板

- `GET /management/dashboard/summary`
- `GET /management/dashboard/checkin-trend`
- `GET /management/dashboard/spot-ranking`
- `GET /management/dashboard/latest-events`
- `GET /management/dashboard/device-status`

全部支持 `scene_id` 和时间范围；“今日”按 Scene 时区计算。

#### 用户

- `GET /management/users`
- `GET /management/users/{user_id}`
- `GET /management/users/{user_id}/cards`
- `GET /management/users/{user_id}/visits`
- `GET /management/users/{user_id}/checkins`

#### 卡片与绑定

- `GET|POST /management/cards`
- `GET|PATCH /management/cards/{card_id}`
- `POST /management/cards/import-preview`
- `POST /management/cards/import-confirm`
- `POST /management/cards/{card_id}/activation-codes`
- `GET /management/cards/{card_id}/bindings`
- `GET /management/cards/{card_id}/checkins`
- `POST /management/bindings/{binding_id}/force-unbind`

#### 场景、点位和路线

- `GET|POST /management/scenes`
- `GET|PATCH /management/scenes/{scene_id}`
- `GET|POST /management/spots`
- `GET|PATCH /management/spots/{spot_id}`
- `POST /management/spots/{spot_id}/publish`
- `POST /management/spots/{spot_id}/disable`
- `GET /management/spots/{spot_id}/statistics`
- `GET /management/spots/{spot_id}/checkins`
- `GET|POST /management/routes`
- `GET|PATCH /management/routes/{route_id}`

#### 设备、游览和事件

- `GET|POST /management/devices`
- `GET|PATCH /management/devices/{device_id}`
- `POST /management/devices/{device_id}/rotate-secret`
- `GET /management/devices/{device_id}/checkins`
- `GET /management/visits`
- `GET /management/visits/{visit_id}`
- `GET /management/checkins`
- `GET /management/checkins/{event_id}`
- `GET /management/audit-logs`

管理列表只返回脱敏用户和卡片信息。高风险写操作必须二次确认、填写原因并创建 `AuditLog`。

## 6. 关键服务与数据流

### 6.1 绑卡事务

1. 当前用户通过 JWT 鉴权。
2. 标准化 UID 并计算 HMAC。
3. 在事务中锁定 Card 和激活码。
4. 校验卡状态和卡片无其他有效绑定；手输 UID 时再校验激活码匹配且未使用。
5. 创建有效 `CardBinding`；手输 UID 时同时消费激活码。
6. 如果用户原本没有主要卡，将新绑定设为主要卡。
7. 返回脱敏卡片和绑定信息。

并发绑定同一张卡只能有一个请求成功；数据库条件唯一约束作为最终保护。

### 6.2 打卡事务

1. 验证时间窗、Nonce、签名和设备状态。
2. 校验设备当前 Spot 与请求 `spot_id` 一致。
3. 查询 `(device, event_id)`；存在则返回其 `result_snapshot`。
4. 标准化 UID、计算 HMAC并查询 Card 和当前绑定。
5. 对合法卡片获取绑定用户。
6. 按 Scene 时区取得或创建当日 `VisitSession`。
7. 创建 `accepted` 事件并更新会话及卡片最近使用时间；业务失败则创建 `rejected` 事件。
8. 保存脱敏 `result_snapshot` 并返回设备反馈码。

整个幂等判断和事件创建在数据库事务中完成。

### 6.3 查询口径

- 用户路线：会话中 `accepted` 事件按 `received_at` 排序，每个 Spot 只取首次；
- 用户完成度：上述不同可打卡 Spot 数 / 当前 Scene 已发布且参与统计的 Spot 数；
- 卡片记录：按 `card_id` 查询事件，不受后续解绑影响；
- 点位访问人数：时间范围内 `accepted` 事件的不同 `user_id` 数；
- 点位打卡次数：时间范围内 `accepted` 事件数；
- 设备事件量：按设备统计接受和拒绝事件；
- 今日游客：当天至少有一条 `accepted` 事件的不同用户数。

## 7. Agent 扩展边界

第一阶段不实现 Dify 调用，但后端业务代码必须提供与 HTTP View 解耦的查询服务，例如：

- `get_current_visit(user, scene)`；
- `get_checkin_progress(user, session)`；
- `get_route_timeline(user, session)`；
- `list_user_checkins(user, filters)`；
- `list_unvisited_spots(user, scene)`；
- `get_spot_detail(spot)`；
- `recommend_next_spots(user, scene, preferences)`。

小程序 View、管理 API 和未来 Agent 工具使用这些服务或专门的管理查询层，不在各自代码中重复拼装业务规则。

未来 Agent 工具必须满足：

- 用户身份来自后端限权上下文，不接受模型任意指定 `user_id`；
- 仅返回当前用户有权访问的 accepted 事实和已发布点位资料；
- 不返回完整 UID、激活码、微信 `openid` 或设备凭据；
- 不允许创建、修改或删除打卡事件；
- 游记生成保存当时使用的路线与点位 `source_snapshot`。

## 8. 错误码

### 8.1 通用

- `AUTH_REQUIRED`
- `TOKEN_INVALID`
- `PERMISSION_DENIED`
- `VALIDATION_ERROR`
- `RESOURCE_NOT_FOUND`
- `CONFLICT`
- `RATE_LIMITED`
- `SERVICE_UNAVAILABLE`

### 8.2 卡片

- `CARD_NOT_FOUND`
- `CARD_DISABLED`
- `CARD_ALREADY_BOUND`
- `ACTIVATION_CODE_INVALID`
- `ACTIVATION_CODE_USED`
- `ACTIVATION_CODE_EXPIRED`
- `BINDING_NOT_FOUND`
- `BINDING_ALREADY_INACTIVE`
- `LAST_PRIMARY_CARD_CHANGED`

### 8.3 设备与打卡

- `DEVICE_UNAUTHORIZED`
- `DEVICE_DISABLED`
- `SIGNATURE_INVALID`
- `REQUEST_EXPIRED`
- `NONCE_REPLAYED`
- `SPOT_MISMATCH`
- `CARD_UNREGISTERED`
- `CARD_UNBOUND`
- `EVENT_ACCEPTED`
- `EVENT_DUPLICATE`
- `EVENT_REJECTED`

错误码稳定，中文 `message` 可以优化；前端逻辑不得依赖文案字符串。

## 9. 安全与隐私

- JWT、微信密钥、UID HMAC 密钥、设备主密钥和真实设备密钥只保存在后端环境或受控存储；
- 日志不记录完整 UID、激活码、令牌、设备密钥或微信临时 code；
- 游客接口始终从当前认证用户确定数据范围；
- 管理端按角色授权，并对解绑、激活码、设备密钥和停用操作写审计；
- 所有输入执行长度、格式和枚举白名单校验；
- 绑卡和设备接口进行限流；
- Demo 数据与真实用户数据使用不同环境和标记。

## 10. 测试与验收

### 10.1 模型与服务测试

- 一个用户可同时绑定两张及以上卡；
- 同一张卡不能同时绑定两个用户；
- 每个用户最多一张主要卡；
- 激活码只能成功消费一次；
- 主要卡解绑后正确选择替代卡；
- 同一用户不同卡当天进入同一会话；
- 次日首条打卡创建新会话；
- 同点重复打卡不增加完成度；
- 同一设备事件重传不新增记录。

### 10.2 API 与权限测试

- 用户不能读取其他用户的卡、游览和打卡；
- 解绑后仍可在本人历史记录中看到原事件；
- 管理端可按用户、卡片、点位、设备和日期筛选；
- 普通管理列表不泄露完整 UID、激活码或微信标识；
- 正式配置下 `/auth/dev-login` 不存在；
- 无效设备签名不创建业务事件；
- 重复事件返回首次处理结果。

### 10.3 Demo 端到端验收

1. Demo 用户登录。
2. 账号依次绑定两张测试卡，并设置主要卡。
3. 两张卡分别在不同点位通过 ESP32 完成真实刷卡。
4. 小程序首页显示同一用户当天汇总进度。
5. 小程序可以按具体卡查看各自记录。
6. 重传相同 `event_id` 不增加记录和完成度。
7. 管理端用户详情显示两张卡和汇总路线。
8. 管理端卡片详情显示该卡事件。
9. 管理端点位详情显示访问人数和打卡次数。
10. 管理端设备详情显示最近心跳和事件结果。

## 11. 初始化数据

使用受版本控制的 Django management command 或数据迁移创建：

- 一个江安校区 Scene；
- 八个经团队确认的 Demo Spot；
- 一至两条推荐路线及其点位顺序；
- 至少一台真实测试设备及其点位归属；
- 至少三张测试卡及一次性激活码；
- 一个 Demo 用户和一个管理员账号。

初始化数据不得包含真实生产密钥。设备明文密钥和激活码只在初始化输出中显示一次，并通过安全渠道交给开发者。

## 12. 实施顺序

1. 公共响应、错误码、权限和审计基础；
2. Scene、Spot、SpotMedia、Route 和初始化数据；
3. Card、ActivationCode、CardBinding 与多卡绑定接口；
4. Device、HMAC、心跳与 CheckinEvent；
5. VisitSession、进度、路线和个人记录查询；
6. 小程序首页/地图/绑卡/记录接口联调；
7. 管理端看板及用户/卡片/点位/设备查询；
8. 全链路测试、演示数据、部署和彩排；
9. 基础闭环稳定后再实现媒体、推荐增强和 Agent。
