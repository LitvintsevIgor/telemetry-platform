-- Existing PostgreSQL schema used old columns (device_id, name, code, ...).
-- create_all() does not ALTER tables; drop and recreate for dev, or run once on deploy:
--
--   psql "$DATABASE_URL" -f backend/migrations/recreate_metrics.sql
--
DROP TABLE IF EXISTS metrics;
