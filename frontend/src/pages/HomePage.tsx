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
  captionBelow,
}: {
  pct: number | null
  caption: string
  compact?: boolean
  /** Подпись под строкой с %, по центру (блоки «за месяц» / «за сегодня») */
  captionBelow?: boolean
}) {
  const wrapClass = compact
    ? `${styles.metricChange} ${styles.metricChangeCompact}`
    : captionBelow
      ? `${styles.metricChange} ${styles.metricChangeStacked}`
      : styles.metricChange

  if (pct == null) {
    if (captionBelow) {
      return (
        <div className={wrapClass}>
          <div className={styles.metricChangePctRow}>
            <span className={styles.pct} style={{ color: MUTED }}>
              —
            </span>
          </div>
          <span className={styles.caption}>{caption}</span>
        </div>
      )
    }
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

  if (captionBelow) {
    return (
      <div className={wrapClass}>
        <div className={styles.metricChangePctRow}>
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
        </div>
        <span className={styles.caption}>{caption}</span>
      </div>
    )
  }

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

function CashCardSplit({
  cash,
  card,
  dayCompare,
}: {
  cash: number
  card: number
  dayCompare?: {
    cashPct: number | null
    cardPct: number | null
    caption: string
  }
}) {
  return (
    <div className={styles.splitBottom}>
      <div className={styles.splitCol} aria-label="Наличные">
        <div className={styles.miniLabelRow}>
          <WalletOutlined className={styles.miniIcon} aria-hidden />
          <span>Наличные</span>
        </div>
        <p className={styles.valueXs}>{formatRub(cash)}</p>
        {dayCompare ? (
          <MetricChange
            pct={dayCompare.cashPct}
            caption={dayCompare.caption}
            compact
          />
        ) : null}
      </div>
      <div className={styles.splitCol} aria-label="Безналичная оплата">
        <div className={styles.miniLabelRow}>
          <CreditCardOutlined className={styles.miniIcon} aria-hidden />
          <span>Безнал</span>
        </div>
        <p className={styles.valueXs}>{formatRub(card)}</p>
        {dayCompare ? (
          <MetricChange
            pct={dayCompare.cardPct}
            caption={dayCompare.caption}
            compact
          />
        ) : null}
      </div>
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
              <div className={`${styles.cardBody} ${styles.splitCardBody}`}>
                <div className={styles.splitTop}>
                  <span className={styles.label}>Выручка за месяц</span>
                  <p className={`${styles.valueCenter} ${styles.valueLg}`}>
                    {formatRub(data.current_month_total)}
                  </p>
                  <MetricChange
                    pct={data.month_vs_prev_month_pct}
                    caption={data.month_compare_caption}
                    captionBelow
                  />
                </div>
                <CashCardSplit cash={data.cash_month} card={data.card_month} />
              </div>
            </Card>

            <Card className={styles.card} styles={{ body: { padding: 0 } }}>
              <div className={`${styles.cardBody} ${styles.splitCardBody}`}>
                <div className={styles.splitTop}>
                  <span className={styles.label}>Выручка за сегодня</span>
                  <p className={`${styles.valueCenter} ${styles.valueMd}`}>
                    {formatRub(data.today_total)}
                  </p>
                  <MetricChange
                    pct={data.today_vs_weekday_pct}
                    caption={data.today_compare_caption}
                    captionBelow
                  />
                </div>
                <CashCardSplit
                  cash={data.cash_today}
                  card={data.card_today}
                  dayCompare={{
                    cashPct: data.cash_vs_yesterday_pct,
                    cardPct: data.card_vs_yesterday_pct,
                    caption: data.day_compare_caption,
                  }}
                />
              </div>
            </Card>
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
