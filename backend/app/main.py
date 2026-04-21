from datetime import datetime

import asyncio
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from settings import settings
from app.db import engine, SessionLocal
from app.models import Base, Metric
from app.month_metrics import compute_dashboard_metrics
from app.poller import poll_external_api
from app import owen_token_store

app = FastAPI(title="Telemetry Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginBody(BaseModel):
    login: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class MetricOut(BaseModel):
    id: int
    timestamp: datetime
    box_id: int
    payment_type: str
    value: float

    model_config = ConfigDict(from_attributes=True)


class MonthSummaryOut(BaseModel):
    """Выручка и сравнения; границы суток и месяца — Europe/Moscow."""

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
    sum_as_of_end_previous_month: float
    start_current_month_msk: datetime


def _require_owen_bearer(authorization: str | None = Header(None)) -> None:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization[7:].strip()
    if owen_token_store.get() != token:
        raise HTTPException(status_code=401, detail="Unauthorized")


OWEN_AUTH_OPEN = "https://api.owencloud.ru/v1/auth/open"


@app.post("/login")
async def login(body: LoginBody):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            OWEN_AUTH_OPEN,
            json={"login": body.login, "password": body.password},
        )
    try:
        payload = response.json()
    except Exception:
        payload = {}
    token = payload.get("token") if isinstance(payload, dict) else None
    if response.status_code != 200 or not token:
        return JSONResponse(status_code=401, content={"success": False})
    owen_token_store.set_token(token)
    return JSONResponse(
        status_code=200,
        content={"success": True, "token": token},
    )


Base.metadata.create_all(bind=engine)


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/metrics", response_model=list[MetricOut])
def get_metrics(box_id: int | None = Query(None)):
    db = SessionLocal()
    try:
        q = db.query(Metric).order_by(Metric.timestamp)
        if box_id is not None:
            q = q.filter(Metric.box_id == box_id)
        return q.all()
    finally:
        db.close()


@app.get("/metrics/month-summary", response_model=MonthSummaryOut)
def get_metrics_month_summary(_: None = Depends(_require_owen_bearer)):
    db = SessionLocal()
    try:
        d = compute_dashboard_metrics(db)
        return MonthSummaryOut(
            current_month_total=d.current_month_total,
            month_vs_prev_month_pct=d.month_vs_prev_month_pct,
            month_compare_caption=d.month_compare_caption,
            today_total=d.today_total,
            today_vs_weekday_pct=d.today_vs_weekday_pct,
            today_compare_caption=d.today_compare_caption,
            cash_today=d.cash_today,
            cash_vs_yesterday_pct=d.cash_vs_yesterday_pct,
            card_today=d.card_today,
            card_vs_yesterday_pct=d.card_vs_yesterday_pct,
            cash_month=d.cash_month,
            card_month=d.card_month,
            day_compare_caption=d.day_compare_caption,
            sum_latest=d.sum_latest,
            sum_as_of_end_previous_month=d.sum_as_of_before_current_month_msk,
            start_current_month_msk=d.start_current_month_msk,
        )
    finally:
        db.close()


scheduler = BackgroundScheduler()

scheduler.add_job(
    lambda: asyncio.run(poll_external_api()),
    "interval",
    seconds=settings.OWEN_POLL_INTERVAL_SECONDS,
)


@app.on_event("startup")
async def startup():
    scheduler.start()


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
