"""Снимки счётчиков и выручка по периодам (Europe/Moscow для календарных границ).

Для каждой пары (box_id, payment_type) из боксов 1–4 и типов cash/card берётся
последняя запись по timestamp не позже заданного момента; если записей нет,
вклад пары 0.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import text
from sqlalchemy.orm import Session

MSK = ZoneInfo("Europe/Moscow")

_EPS = timedelta(microseconds=1)


def _naive_utc(dt: datetime) -> datetime:
    """timestamp в БД — naive UTC (как в poller)."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def _payment_in_clause(payment_types: tuple[str, ...]) -> str:
    if payment_types == ("cash", "card"):
        return "'cash', 'card'"
    if payment_types == ("cash",):
        return "'cash'"
    if payment_types == ("card",):
        return "'card'"
    raise ValueError("payment_types must be ('cash','card'), ('cash',) or ('card',)")


def sum_counters_as_of(db: Session, t_end: datetime, payment_types: tuple[str, ...]) -> float:
    """Сумма последних значений счётчиков по всем парам (box, type) с timestamp <= t_end."""
    t_end = _naive_utc(t_end)
    pt = _payment_in_clause(payment_types)
    stmt = text(
        f"""
        SELECT COALESCE(SUM(s.v), 0.0)
        FROM (
            SELECT DISTINCT ON (box_id, payment_type) value AS v
            FROM metrics
            WHERE box_id BETWEEN 1 AND 4
              AND payment_type IN ({pt})
              AND "timestamp" <= :t_end
            ORDER BY box_id, payment_type, "timestamp" DESC NULLS LAST
        ) s
        """
    )
    row = db.execute(stmt, {"t_end": t_end}).one()
    return float(row[0])


def start_of_day_msk(d: datetime.date) -> datetime:
    """Первый момент календарного дня в MSK (aware)."""
    return datetime.combine(d, time.min, tzinfo=MSK)


def start_of_month_msk(d: datetime.date) -> datetime:
    """Первый момент календарного месяца, содержащего дату d (MSK)."""
    return datetime(d.year, d.month, 1, 0, 0, 0, tzinfo=MSK)


def end_of_previous_day_msk(day: datetime.date) -> datetime:
    """Последний момент дня перед `day` в MSK (aware)."""
    return start_of_day_msk(day) - _EPS


def same_calendar_moment_prev_month_msk(now_msk: datetime) -> datetime:
    """Тот же день и время в предыдущем календарном месяце (день клампится к концу месяца)."""
    y, m, d = now_msk.year, now_msk.month, now_msk.day
    if m == 1:
        y, m = y - 1, 12
    else:
        m -= 1
    max_day = calendar.monthrange(y, m)[1]
    day = min(d, max_day)
    return datetime(
        y,
        m,
        day,
        now_msk.hour,
        now_msk.minute,
        now_msk.second,
        now_msk.microsecond,
        tzinfo=MSK,
    )


def pct_or_none(current: float, baseline: float) -> float | None:
    if baseline == 0.0:
        return None
    return (current - baseline) / baseline * 100.0


# День недели для даты «неделю назад»: полная подпись для UI (к прошлому …)
_WEEKDAY_COMPARE_CAPTION = (
    "к прошлому понедельнику",
    "к прошлому вторнику",
    "к прошлой среде",
    "к прошлому четвергу",
    "к прошлой пятнице",
    "к прошлой субботе",
    "к прошлому воскресенью",
)


def weekday_compare_caption_for_date(d: datetime.date) -> str:
    """d — календарный день, с которым сравниваем (обычно сегодня − 7 дней)."""
    return _WEEKDAY_COMPARE_CAPTION[d.weekday()]


@dataclass(frozen=True)
class DashboardMetrics:
    current_month_total: float
    month_vs_prev_month_pct: float | None
    month_compare_caption: str

    today_total: float
    today_vs_weekday_pct: float | None
    today_compare_caption: str

    cash_today: float
    cash_vs_yesterday_pct: float | None

    card_today: float
    card_vs_yesterday_pct: float | None

    cash_month: float
    card_month: float

    day_compare_caption: str

    sum_latest: float
    # сумма счётчиков на момент непосредственно перед началом текущего месяца (MSK)
    sum_as_of_before_current_month_msk: float
    start_current_month_msk: datetime


def compute_dashboard_metrics(db: Session, now_utc: datetime | None = None) -> DashboardMetrics:
    now_utc = now_utc or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    else:
        now_utc = now_utc.astimezone(timezone.utc)

    now_msk = now_utc.astimezone(MSK)
    today_msk = now_msk.date()

    start_current_month = start_of_month_msk(today_msk)
    sum_now_all = sum_counters_as_of(db, now_utc, ("cash", "card"))
    sum_before_month = sum_counters_as_of(db, start_current_month - _EPS, ("cash", "card"))
    month_total = sum_now_all - sum_before_month

    sum_before_month_cash = sum_counters_as_of(db, start_current_month - _EPS, ("cash",))
    sum_before_month_card = sum_counters_as_of(db, start_current_month - _EPS, ("card",))

    prev_month_moment = same_calendar_moment_prev_month_msk(now_msk)
    prev_month_start = start_of_month_msk(prev_month_moment.date())
    sum_prev_end = sum_counters_as_of(db, prev_month_moment, ("cash", "card"))
    sum_prev_start = sum_counters_as_of(db, prev_month_start - _EPS, ("cash", "card"))
    month_prev = sum_prev_end - sum_prev_start
    month_pct = pct_or_none(month_total, month_prev)

    end_yesterday = end_of_previous_day_msk(today_msk)
    sum_today_all = sum_now_all - sum_counters_as_of(db, end_yesterday, ("cash", "card"))

    week_ago = now_msk - timedelta(days=7)
    week_day = week_ago.date()
    week_start = start_of_day_msk(week_day)
    sum_week_end = sum_counters_as_of(db, week_ago, ("cash", "card"))
    sum_week_start = sum_counters_as_of(db, week_start - _EPS, ("cash", "card"))
    week_ref = sum_week_end - sum_week_start
    today_pct = pct_or_none(sum_today_all, week_ref)

    sum_now_cash = sum_counters_as_of(db, now_utc, ("cash",))
    cash_month = sum_now_cash - sum_before_month_cash

    sum_now_card = sum_counters_as_of(db, now_utc, ("card",))
    card_month = sum_now_card - sum_before_month_card

    sum_end_y_cash = sum_counters_as_of(db, end_yesterday, ("cash",))
    cash_today = sum_now_cash - sum_end_y_cash
    before_yesterday = end_of_previous_day_msk(today_msk - timedelta(days=1))
    cash_yesterday = sum_end_y_cash - sum_counters_as_of(db, before_yesterday, ("cash",))
    cash_pct = pct_or_none(cash_today, cash_yesterday)

    sum_end_y_card = sum_counters_as_of(db, end_yesterday, ("card",))
    card_today = sum_now_card - sum_end_y_card
    card_yesterday = sum_end_y_card - sum_counters_as_of(db, before_yesterday, ("card",))
    card_pct = pct_or_none(card_today, card_yesterday)

    return DashboardMetrics(
        current_month_total=month_total,
        month_vs_prev_month_pct=month_pct,
        month_compare_caption="к прошлому месяцу",
        today_total=sum_today_all,
        today_vs_weekday_pct=today_pct,
        today_compare_caption=weekday_compare_caption_for_date(week_day),
        cash_today=cash_today,
        cash_vs_yesterday_pct=cash_pct,
        card_today=card_today,
        card_vs_yesterday_pct=card_pct,
        cash_month=cash_month,
        card_month=card_month,
        day_compare_caption="от вчера",
        sum_latest=sum_now_all,
        sum_as_of_before_current_month_msk=sum_before_month,
        start_current_month_msk=start_current_month,
    )


