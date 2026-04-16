import { apiBaseUrl } from './client'

export type MonthSummary = {
  current_month_total: number
  month_vs_prev_month_pct: number | null
  month_compare_caption: string

  today_total: number
  today_vs_weekday_pct: number | null
  today_compare_caption: string

  cash_today: number
  cash_vs_yesterday_pct: number | null

  card_today: number
  card_vs_yesterday_pct: number | null

  day_compare_caption: string

  sum_latest: number
  sum_as_of_end_previous_month: number
  start_current_month_msk: string
}

export async function getMonthSummary(token: string): Promise<MonthSummary> {
  const res = await fetch(`${apiBaseUrl()}/metrics/month-summary`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const data = (await res.json().catch(() => ({}))) as Record<string, unknown>
  if (!res.ok) {
    const detail =
      typeof data.detail === 'string' ? data.detail : 'Не удалось загрузить показатели'
    throw new Error(detail)
  }
  return data as unknown as MonthSummary
}
