import {
  CreditCardOutlined,
  FallOutlined,
  RiseOutlined,
  WalletOutlined,
} from '@ant-design/icons'
import { useEffect, useState } from 'react'
import { Button, Card, Flex, Spin, Typography } from 'antd'
import { Navigate, useNavigate } from 'react-router-dom'
import { getMonthSummary } from '../api/monthSummary'
import { AUTH_TOKEN_KEY } from '../constants/auth'
import styles from './HomePage.module.css'

const IOS_GREEN = '#34C759'
const IOS_RED = '#FF3B30'
const MUTED = 'rgba(60, 60, 67, 0.45)'

function formatRub(n: number) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(n)
}

function MetricChange({
  pct,
  caption,
  compact,
}: {
  pct: number | null
  caption: string
  compact?: boolean
}) {
  const wrapClass = compact
    ? `${styles.metricChange} ${styles.metricChangeCompact}`
    : styles.metricChange

  if (pct == null) {
    return (
      <div className={wrapClass}>
        <span className={styles.pct} style={{ color: MUTED }}>
          —
        </span>
        <span className={styles.caption}>{caption}</span>
      </div>
    )
  }

  const positive = pct > 0
  const negative = pct < 0
  const neutral = pct === 0
  const color = neutral ? MUTED : positive ? IOS_GREEN : IOS_RED

  return (
    <div className={wrapClass}>
      {!neutral && positive && (
        <RiseOutlined
          className={styles.arrow}
          style={{ color: IOS_GREEN, fontSize: 11 }}
          aria-hidden
        />
      )}
      {!neutral && negative && (
        <FallOutlined
          className={styles.arrow}
          style={{ color: IOS_RED, fontSize: 11 }}
          aria-hidden
        />
      )}
      <span className={styles.pct} style={{ color }}>
        {positive ? '+' : ''}
        {pct.toFixed(1)}%
      </span>
      <span className={styles.caption}>{caption}</span>
    </div>
  )
}

export default function HomePage() {
  const navigate = useNavigate()
  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  const [data, setData] = useState<Awaited<ReturnType<typeof getMonthSummary>> | null>(
    null,
  )
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) {
      return
    }
    const authToken = token
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const res = await getMonthSummary(authToken)
        if (!cancelled) {
          setData(res)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Ошибка загрузки')
          setData(null)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [token])

  if (!token) {
    return <Navigate to="/login" replace />
  }

  const logout = () => {
    localStorage.clear()
    navigate('/login', { replace: true })
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {loading ? (
          <Flex justify="center" style={{ padding: 48 }}>
            <Spin size="large" />
          </Flex>
        ) : error ? (
          <Typography.Text type="danger">{error}</Typography.Text>
        ) : data ? (
          <div className={styles.stack}>
            <Card className={styles.card} styles={{ body: { padding: 0 } }}>
              <div className={`${styles.cardBody} ${styles.cardCenter}`}>
                <span className={styles.label}>Выручка за месяц</span>
                <p className={`${styles.valueCenter} ${styles.valueLg}`}>
                  {formatRub(data.current_month_total)}
                </p>
                <MetricChange
                  pct={data.month_vs_prev_month_pct}
                  caption={data.month_compare_caption}
                />
              </div>
            </Card>

            <Card className={styles.card} styles={{ body: { padding: 0 } }}>
              <div className={`${styles.cardBody} ${styles.cardCenter}`}>
                <span className={styles.label}>Выручка сегодня</span>
                <p className={`${styles.valueCenter} ${styles.valueMd}`}>
                  {formatRub(data.today_total)}
                </p>
                <MetricChange
                  pct={data.today_vs_weekday_pct}
                  caption={data.today_compare_caption}
                />
              </div>
            </Card>

            <div className={styles.pairRow}>
              <Card
                className={`${styles.card} ${styles.cardMini}`}
                styles={{ body: { padding: 0 } }}
                aria-label="Наличные за сегодня"
              >
                <div className={styles.cardMiniInner}>
                  <div className={styles.miniLabelRow}>
                    <WalletOutlined className={styles.miniIcon} aria-hidden />
                    <span>за сегодня</span>
                  </div>
                  <p className={styles.valueXs}>{formatRub(data.cash_today)}</p>
                  <MetricChange
                    pct={data.cash_vs_yesterday_pct}
                    caption={data.day_compare_caption}
                    compact
                  />
                </div>
              </Card>
              <Card
                className={`${styles.card} ${styles.cardMini}`}
                styles={{ body: { padding: 0 } }}
                aria-label="Безналичная оплата за сегодня"
              >
                <div className={styles.cardMiniInner}>
                  <div className={styles.miniLabelRow}>
                    <CreditCardOutlined className={styles.miniIcon} aria-hidden />
                    <span>за сегодня</span>
                  </div>
                  <p className={styles.valueXs}>{formatRub(data.card_today)}</p>
                  <MetricChange
                    pct={data.card_vs_yesterday_pct}
                    caption={data.day_compare_caption}
                    compact
                  />
                </div>
              </Card>
            </div>
          </div>
        ) : null}
      </div>

      <Flex justify="center" style={{ marginTop: 20 }}>
        <Button type="text" className={styles.logout} onClick={logout}>
          Выйти
        </Button>
      </Flex>
    </div>
  )
}
