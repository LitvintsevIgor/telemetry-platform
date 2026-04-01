from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel, Field
import asyncio
import httpx

from settings import settings
from app.db import engine, SessionLocal
from app.models import Base, Metric
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