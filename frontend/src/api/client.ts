export function apiBaseUrl(): string {
  const base = import.meta.env.VITE_API_URL
  if (!base) {
    throw new Error('VITE_API_URL is not set')
  }
  return base.replace(/\/$/, '')
}
