# Web 管理端

“游迹织梦”展示与运营管理端，基于 Vue 3、TypeScript、Pinia 和 Element Plus。

## 本地环境

- Node.js：24 LTS
- 后端地址：`http://localhost:8000`
- 前端地址：`http://localhost:5173`
- 演示用户名：`demo_admin`
- 演示密码：`TravelWeave-Demo-2026!`
- 使用限制：演示账号仅允许本地 `DEBUG=True` 环境登录，生产环境会拒绝该账号。

首次运行：

```bash
cp .env.example .env.local
npm ci
npm run dev
```

质量检查：

```bash
npm test
npm run type-check
npm run build
```

启动管理端前必须先迁移并启动 Django 后端。管理端不得保存数据库密码、设备密钥、
激活码、完整卡片 UID 或模型服务密钥。设备密钥和卡片激活码只在生成弹窗中显示一次。
