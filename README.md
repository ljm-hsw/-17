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

后端是前端团队的稳定契约边界。首次启动并执行 `seed_jiang_an_demo` 后，可在
`http://127.0.0.1:8000/api/docs/` 查看接口，并使用固定的江安场景、点位、路线、
卡片和设备数据开发管理端与微信小程序。前端成员不直接读取或修改数据库。

## 本地启动

只有在开发真实数据功能时才需要启动 PostgreSQL；它不要求平时常驻运行：

```bash
docker compose --env-file infra/.env.example -f infra/compose.yaml up -d postgres
```

各端分别在独立终端按需启动：

```bash
cd backend && cp .env.example .env && .venv/bin/python manage.py migrate && .venv/bin/python manage.py seed_jiang_an_demo && .venv/bin/python manage.py runserver
cd admin-web && npm ci && npm run dev
cd miniprogram && npm ci && npm run dev:mp-weixin
cd firmware && pio run -e esp32dev
```

## 设计依据

- [产品与业务规则](docs/superpowers/specs/2026-07-13-jiang-an-mvp-product-business-design.md)
- [技术架构与数据设计](docs/superpowers/specs/2026-07-13-jiang-an-mvp-technical-architecture.md)
- [Web 管理端设计](docs/superpowers/specs/2026-07-21-admin-web-design.md)
- [v2 工程框架实施计划](docs/superpowers/plans/2026-07-21-v2-bootstrap-implementation-plan.md)
