# Infrastructure

本目录维护本地开发和后续部署所需的基础设施配置。当前提供 PostgreSQL 16。

## 启动

```bash
cp infra/.env.example infra/.env
docker compose --env-file infra/.env -f infra/compose.yaml up -d postgres
docker compose --env-file infra/.env -f infra/compose.yaml ps
```

首次启动后，在 `backend/` 复制环境变量并运行迁移：

```bash
cp backend/.env.example backend/.env
backend/.venv/bin/python backend/manage.py migrate
```

## 停止

```bash
docker compose --env-file infra/.env -f infra/compose.yaml down
```

只有在确认不再需要本地数据时才使用 `down -v`。
