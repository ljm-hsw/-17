import { readdir, rm, stat } from 'node:fs/promises'
import { extname, join, resolve } from 'node:path'
import { loadViteProductionEnv } from './env.mjs'

const env = loadViteProductionEnv()
const assetBaseUrl = (env.VITE_ASSET_BASE_URL ?? '').trim()

if (!assetBaseUrl) {
  console.log('[remote-assets] VITE_ASSET_BASE_URL is empty; keeping local images.')
  process.exit(0)
}

if (!/^https:\/\//i.test(assetBaseUrl)) {
  throw new Error('VITE_ASSET_BASE_URL must be an HTTPS URL for a WeChat submission build.')
}

const outputRoot = resolve(process.cwd(), 'dist/build/mp-weixin/static')
const remoteExtensions = new Set(['.avif', '.gif', '.jpeg', '.jpg', '.png', '.webp'])
const localRasterPaths = new Set(['guide/tubiao.png'])
let removedBytes = 0
let removedFiles = 0

async function prune(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) {
      await prune(path)
      continue
    }
    const relativePath = path.slice(outputRoot.length + 1).replaceAll('\\', '/')
    if (
      localRasterPaths.has(relativePath) ||
      !remoteExtensions.has(extname(entry.name).toLowerCase())
    ) continue
    removedBytes += (await stat(path)).size
    removedFiles += 1
    await rm(path)
  }
}

await prune(outputRoot)
console.log(
  `[remote-assets] Removed ${removedFiles} raster files (${(removedBytes / 1024 / 1024).toFixed(2)} MiB) from the WeChat package.`,
)
