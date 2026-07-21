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
