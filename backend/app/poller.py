from settings import settings
import httpx
import asyncio
from datetime import datetime

from app.db import SessionLocal
from app.models import Metric

LOGIN = settings.OWEN_LOGIN
PASSWORD = settings.OWEN_PASSWORD
PARAMETER_ID = settings.OWEN_PARAMETER_ID

async def poll_external_api():

    async with httpx.AsyncClient() as client:

        # 1️⃣ Авторизация
        login_response = await client.post(
            "https://api.owencloud.ru/v1/auth/open",
            json={
                "login": LOGIN,
                "password": PASSWORD
            }
        )

        token = login_response.json().get("token")

        if not token:
            print("Failed to get token")
            return

        # 2️⃣ Запрос параметра
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "*/*",
            "Content-Type": "application/json"
        }

        response = await client.post(
            "https://api.owencloud.ru/v1/parameters/last-data",
            headers=headers,
            json={"ids": [PARAMETER_ID]}
        )

        data = response.json()

        if data and data[0]["values"]:
            value = data[0]["values"][0]["v"]
        else:
            print("No data received")
            return

        print("Received data:", data)

        value = data[0]["values"][0]["v"]

        print("Received value:", value)

        # 3️⃣ Сохраняем в БД
        db = SessionLocal()

        try:
            metric = Metric(
                device_id=PARAMETER_ID,
                name="Общая выручка",
                code="f88",
                value=value,
                timestamp=datetime.utcnow()
            )

            db.add(metric)
            db.commit()

        finally:
            db.close()