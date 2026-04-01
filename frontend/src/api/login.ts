import { apiBaseUrl } from './client'

export type LoginPayload = {
  login: string
  password: string
}

export type LoginSuccess = {
  success: true
  token: string
}

export async function postLogin(body: LoginPayload): Promise<LoginSuccess> {
  const res = await fetch(`${apiBaseUrl()}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = (await res.json().catch(() => ({}))) as Record<string, unknown>
  if (!res.ok || data.success !== true || typeof data.token !== 'string') {
    throw new Error(
      typeof data.detail === 'string'
        ? data.detail
        : 'Не удалось войти. Проверьте логин и пароль.',
    )
  }
  return { success: true, token: data.token }
}
