# 小程序图片迁移到腾讯云 COS

小程序位图统一上传到腾讯云 COS，本地开发仍使用 `src/static` 中的图片。配置
`VITE_ASSET_BASE_URL` 后，运行微信生产构建会将代码中的位图地址切换为 HTTPS
链接，并自动从提交包删除对应图片。SVG 图标和地图原生标记图保留在包内。

## 1. 准备 COS

1. 创建成都地域（或离服务器最近地域）的 COS 存储桶。
2. 为比赛演示使用的图片配置公开读，或绑定具有公开读权限的 CDN 域名。
3. 创建只允许向指定存储桶上传对象的临时密钥或子账号密钥，不要使用主账号密钥。
4. 把 `.env.cos.example` 复制为 `.env.cos.local`，填写桶名、地域和临时密钥。

`.env.cos.local` 已被 Git 忽略，不会提交到仓库。

## 2. 检查并上传

```bash
cd miniprogram
npm run assets:upload:cos:dry-run
npm run assets:upload:cos
```

脚本会上传 `src/static` 中的 PNG/JPEG/GIF/WebP/AVIF，并为对象设置一年缓存。
上传结束会打印 `VITE_ASSET_BASE_URL` 的值。

## 3. 配置并构建

在 `miniprogram/.env.local` 增加上传脚本打印的地址，例如：

```dotenv
VITE_ASSET_BASE_URL=https://travelweave-1250000000.cos.ap-chengdu.myqcloud.com/travelweave
```

然后构建：

```bash
npm run build:mp-weixin
```

只有 `VITE_ASSET_BASE_URL` 是有效 HTTPS 地址时才会裁剪提交包。本地未配置时，
程序继续使用本地图片，不影响开发。

## 4. 微信后台域名

在微信公众平台的“小程序后台 → 开发管理 → 开发设置 → 服务器域名”中，把 COS
域名或 CDN 域名加入 `downloadFile` 合法域名。正式提交前用真机预览，确认全部图片
能加载；开发者工具中的“不校验合法域名”不会替代后台配置。
