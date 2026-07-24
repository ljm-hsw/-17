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
