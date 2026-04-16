-- Схема должна совпадать с backend/app/models.py (Metric).
-- Старые таблицы без box_id / payment_type ломают /metrics/month-summary.
--
-- ВНИМАНИЕ: удаляет все строки в metrics.
--
-- Один раз на проде (Neon / Railway Postgres / локально):
--   psql "$DATABASE_URL" -f backend/migrations/recreate_metrics.sql
--
DROP TABLE IF EXISTS metrics;

CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE,
    box_id INTEGER NOT NULL,
    payment_type VARCHAR NOT NULL,
    value DOUBLE PRECISION NOT NULL
);

CREATE INDEX ix_metrics_timestamp ON metrics (timestamp);
CREATE INDEX ix_metrics_box_id ON metrics (box_id);
CREATE INDEX ix_metrics_payment_type ON metrics (payment_type);
