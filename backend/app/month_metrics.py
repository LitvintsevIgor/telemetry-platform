"""Прирост с начала текущего календарного месяца по снимкам счётчиков.

Граница месяцев — UTC. Для каждой пары (box_id, payment_type) из боксов 1–4 и
типов cash/card берётся последняя запись по timestamp; если до конца прошлого
месяца строк нет, вклад этой пары в «сумму тогда» равен 0 (через отсутствие
строк в подзапросе).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session


def end_of_previous_month_utc(now: datetime | None = None) -> datetime:
    """Последний момент предыдущего календарного месяца (UTC), для сравнения с timestamp."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)
    first_this_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    return first_this_month - timedelta(microseconds=1)


_SUM_LATEST = text(
    """
    SELECT COALESCE(SUM(s.v), 0.0)
    FROM (
        SELECT DISTINCT ON (box_id, payment_type) value AS v
        FROM metrics
        WHERE box_id BETWEEN 1 AND 4
          AND payment_type IN ('cash', 'card')
        ORDER BY box_id, payment_type, "timestamp" DESC NULLS LAST
    ) s
    """
)

_SUM_AS_OF = text(
    """
    SELECT COALESCE(SUM(s.v), 0.0)
    FROM (
        SELECT DISTINCT ON (box_id, payment_type) value AS v
        FROM metrics
        WHERE box_id BETWEEN 1 AND 4
          AND payment_type IN ('cash', 'card')
          AND "timestamp" <= :t_end
        ORDER BY box_id, payment_type, "timestamp" DESC NULLS LAST
    ) s
    """
)


def month_summary_values(db: Session, t_end: datetime) -> tuple[float, float, float]:
    """Возвращает (sum_latest, sum_as_of_t_end, current_month_increment)."""
    row_now = db.execute(_SUM_LATEST).one()
    sum_latest = float(row_now[0])

    row_then = db.execute(_SUM_AS_OF, {"t_end": t_end}).one()
    sum_as_of = float(row_then[0])

    return sum_latest, sum_as_of, sum_latest - sum_as_of
