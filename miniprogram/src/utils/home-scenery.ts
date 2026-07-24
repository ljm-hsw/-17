export function chunkItems<T>(items: readonly T[], chunkSize: number): readonly (readonly T[])[] {
  if (!Number.isInteger(chunkSize) || chunkSize <= 0 || items.length === 0) {
    return []
  }

  const chunks: T[][] = []
  for (let index = 0; index < items.length; index += chunkSize) {
    chunks.push(items.slice(index, index + chunkSize))
  }
  return chunks
}
