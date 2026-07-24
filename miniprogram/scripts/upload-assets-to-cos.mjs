import { createHash, createHmac } from 'node:crypto'
import { readdir, readFile, stat } from 'node:fs/promises'
import { extname, join, posix, relative, resolve, sep } from 'node:path'
import { loadEnvFile } from './env.mjs'

const fileEnv = loadEnvFile('.env.cos.local')
const env = { ...fileEnv, ...process.env }
const dryRun = process.argv.includes('--dry-run')
const sourceRoot = resolve(process.cwd(), 'src/static')
const imageExtensions = new Set(['.avif', '.gif', '.jpeg', '.jpg', '.png', '.webp'])

const requiredKeys = dryRun
  ? []
  : ['COS_BUCKET', 'COS_REGION', 'COS_SECRET_ID', 'COS_SECRET_KEY']
const missingKeys = requiredKeys.filter((key) => !env[key]?.trim())
if (missingKeys.length > 0) {
  throw new Error(`Missing COS configuration: ${missingKeys.join(', ')}`)
}

const bucket = env.COS_BUCKET?.trim() || 'dry-run-bucket'
const region = env.COS_REGION?.trim() || 'ap-chengdu'
const secretId = env.COS_SECRET_ID?.trim()
const secretKey = env.COS_SECRET_KEY?.trim()
const sessionToken = env.COS_SESSION_TOKEN?.trim()
const prefix = (env.COS_PREFIX ?? 'travelweave').trim().replace(/^\/+|\/+$/g, '')
const objectAcl = (env.COS_OBJECT_ACL ?? 'public-read').trim()
const host = bucket && region ? `${bucket}.cos.${region}.myqcloud.com` : 'dry-run.invalid'
const endpoint = `https://${host}`

const contentTypes = {
  '.avif': 'image/avif',
  '.gif': 'image/gif',
  '.jpeg': 'image/jpeg',
  '.jpg': 'image/jpeg',
  '.png': 'image/png',
  '.webp': 'image/webp',
}

function encode(value) {
  return encodeURIComponent(value).replace(/[!'()*]/g, (char) =>
    `%${char.charCodeAt(0).toString(16).toUpperCase()}`,
  )
}

function hmac(key, value) {
  return createHmac('sha1', key).update(value).digest('hex')
}

function sha1(value) {
  return createHash('sha1').update(value).digest('hex')
}

function authorization(method, pathname, signedHeaders) {
  const now = Math.floor(Date.now() / 1000) - 60
  const keyTime = `${now};${now + 3600}`
  const headerNames = Object.keys(signedHeaders).sort()
  const canonicalHeaders = headerNames
    .map((name) => `${encode(name)}=${encode(signedHeaders[name])}`)
    .join('&')
  const httpString = `${method.toLowerCase()}\n${pathname}\n\n${canonicalHeaders}\n`
  const stringToSign = `sha1\n${keyTime}\n${sha1(httpString)}\n`
  const signature = hmac(hmac(secretKey, keyTime), stringToSign)

  return [
    'q-sign-algorithm=sha1',
    `q-ak=${encode(secretId)}`,
    `q-sign-time=${keyTime}`,
    `q-key-time=${keyTime}`,
    `q-header-list=${headerNames.join(';')}`,
    'q-url-param-list=',
    `q-signature=${signature}`,
  ].join('&')
}

async function findImages(directory) {
  const files = []
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) files.push(...(await findImages(path)))
    else if (imageExtensions.has(extname(entry.name).toLowerCase())) files.push(path)
  }
  return files
}

async function upload(filePath, index, total) {
  const assetPath = relative(sourceRoot, filePath).split(sep).join('/')
  const objectKey = posix.join(prefix, 'static', assetPath)
  const pathname = `/${objectKey.split('/').map(encode).join('/')}`
  const size = (await stat(filePath)).size

  if (dryRun) {
    console.log(`[${index}/${total}] ${objectKey} (${size} bytes)`)
    return
  }

  const signedHeaders = { host }
  if (objectAcl) signedHeaders['x-cos-acl'] = objectAcl
  if (sessionToken) signedHeaders['x-cos-security-token'] = sessionToken

  const headers = {
    Authorization: authorization('PUT', pathname, signedHeaders),
    'Cache-Control': 'public, max-age=31536000, immutable',
    'Content-Type': contentTypes[extname(filePath).toLowerCase()],
    ...signedHeaders,
  }
  const response = await fetch(`${endpoint}${pathname}`, {
    method: 'PUT',
    headers,
    body: await readFile(filePath),
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`COS upload failed for ${objectKey}: ${response.status} ${detail}`)
  }
  console.log(`[${index}/${total}] uploaded ${objectKey}`)
}

const images = (await findImages(sourceRoot)).sort()
let cursor = 0
const workers = Array.from({ length: Math.min(4, images.length) }, async () => {
  while (cursor < images.length) {
    const index = cursor++
    await upload(images[index], index + 1, images.length)
  }
})
await Promise.all(workers)

const publicBaseUrl = (env.COS_PUBLIC_BASE_URL ?? `${endpoint}/${prefix}`).replace(/\/+$/, '')
console.log(`\nUploaded ${images.length} images.`)
console.log(`Set VITE_ASSET_BASE_URL=${publicBaseUrl}`)
