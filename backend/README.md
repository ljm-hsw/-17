# Backend

游迹织梦唯一业务后端，基于 Django 5.2 LTS 与 Django REST Framework。

## 本地开发

推荐使用 PostgreSQL 进行正式联调：

```bash
cd ..
docker compose --env-file infra/.env.example -f infra/compose.yaml up -d postgres
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements/dev.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_jiang_an_demo
.venv/bin/python manage.py runserver
```

API 健康检查：`GET /api/v1/health`；OpenAPI 文档：`GET /api/docs/`。

不启动 PostgreSQL 时，可以使用 SQLite 完成轻量开发验证：

```bash
cp .env.example .env  # 首次运行；设备加密密钥和本地前端来源由此载入
DATABASE_URL=sqlite:///demo.sqlite3 .venv/bin/python manage.py migrate
DATABASE_URL=sqlite:///demo.sqlite3 .venv/bin/python manage.py seed_jiang_an_demo
DATABASE_URL=sqlite:///demo.sqlite3 .venv/bin/python manage.py runserver
```

`seed_jiang_an_demo` 会幂等创建江安校区、8 个点位、2 条路线、3 张测试卡、
1 台演示设备、三类后台角色和一个团队管理端测试账号。新生成的卡片激活码与设备密钥只在命令行显示一次，
不得写入代码、提交记录、截图或群聊。也可以通过
`--device-secret=本地测试密钥` 为 Arduino 联调指定演示设备密钥。

管理端本地测试账号默认为 `demo_admin` / `TravelWeave-Demo-2026!`，可通过
`.env` 中的 `DEMO_ADMIN_USERNAME`、`DEMO_ADMIN_PASSWORD` 和
`DEMO_ADMIN_NICKNAME` 覆盖。该账号标记为 Demo 账号，只允许在
`DEBUG=True` 的开发环境登录；生产环境必须使用单独创建的正式管理员账号。

管理端认证接口为 `POST /api/v1/management/auth/login`，当前管理员与权限接口为
`GET /api/v1/management/auth/me`。

`POST /api/v1/auth/dev-login` 仅在本地 `DEBUG=True` 时可用，生产环境固定返回 404。

## 质量检查

```bash
DATABASE_URL=sqlite://:memory: .venv/bin/pytest -q \
  -k 'not test_v2_is_configured_for_postgresql'
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python manage.py makemigrations --check --dry-run
DATABASE_URL=sqlite://:memory: .venv/bin/python manage.py spectacular \
  --file /tmp/travelweave-openapi.yaml --validate
```

省略 `-k` 并连接 PostgreSQL 后，可执行包含数据库厂商断言在内的完整测试。
