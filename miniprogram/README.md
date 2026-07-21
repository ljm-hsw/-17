# 微信小程序端

基于 uni-app、Vue 3、Vite 和 TypeScript，目标平台为微信小程序。

```bash
npm ci
npm test
npm run dev:mp-weixin
npm run build:mp-weixin
```

复制 `.env.example` 为 `.env.local` 并填写后端地址。微信开发者工具应导入构建生成的 `dist/build/mp-weixin` 目录；真实 AppID 不提交到仓库。

## 依赖维护

使用 DCloud 官方工具 `npx @dcloudio/uvm@latest` 同步正式版编译器。当前 `npm audit` 的剩余高危告警来自 DCloud 上游编译工具链，不能使用 `npm audit fix --force` 强行降级或跨版本修复；升级后必须重新运行微信构建。
