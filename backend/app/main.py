from fastapi import FastAPI, Query
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

from app.db import engine, SessionLocal
from app.models import Base, Metric
from app.poller import poll_external_api

app = FastAPI(title="Telemetry Platform")


# создаем таблицы
Base.metadata.create_all(bind=engine)


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def get_metrics(device_id: str = Query(...)):

    db = SessionLocal()

    try:

        data = db.query(Metric) \
            .filter(Metric.device_id == device_id) \
            .order_by(Metric.timestamp) \
            .all()

        return data

    finally:
        db.close()


scheduler = BackgroundScheduler()

scheduler.add_job(
    lambda: asyncio.run(poll_external_api()),
    "interval",
    seconds=60
)


@app.on_event("startup")
def start_scheduler():
    scheduler.start()


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()