# Backend

游迹织梦唯一业务后端，基于 Django 5.2 LTS 与 Django REST Framework。

## 本地开发

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements/dev.txt
cp .env.example .env
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

API 健康检查：`GET /api/v1/health`；OpenAPI 文档：`GET /api/docs/`。

## 质量检查

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```
