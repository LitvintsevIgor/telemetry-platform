import { apiBaseUrl } from './client'

export type MonthSummary = {
  current_month_total: number
  sum_latest: number
  sum_as_of_end_previous_month: number
  end_previous_month_utc: string
}

export async function getMonthSummary(token: string): Promise<MonthSummary> {
  const res = await fetch(`${apiBaseUrl()}/metrics/month-summary`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const data = (await res.json().catch(() => ({}))) as Record<string, unknown>
  if (!res.ok) {
    const detail =
      typeof data.detail === 'string' ? data.detail : 'Не удалось загрузить сумму за месяц'
    throw new Error(detail)
  }
  return data as unknown as MonthSummary
}
