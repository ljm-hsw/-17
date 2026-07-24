const assetBaseUrl = (import.meta.env.VITE_ASSET_BASE_URL ?? '').trim().replace(/\/+$/, '')

const remoteImagePattern = /^\/static\/.+\.(?:avif|gif|jpe?g|png|webp)(?:[?#].*)?$/i
const localRasterPaths = new Set(['/static/guide/tubiao.png'])

/**
 * Keeps local assets available during development and switches raster images to
 * the configured object-storage origin in submission builds.
 */
export function assetUrl(path: string): string {
  if (!assetBaseUrl || localRasterPaths.has(path) || !remoteImagePattern.test(path)) return path
  return `${assetBaseUrl}${path}`
}

/** Recursively resolves image paths in the static demo-data objects. */
export function withRemoteAssets<T>(value: T): T {
  if (typeof value === 'string') return assetUrl(value) as T
  if (Array.isArray(value)) return value.map((item) => withRemoteAssets(item)) as T
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, withRemoteAssets(item)]),
    ) as T
  }
  return value
}
