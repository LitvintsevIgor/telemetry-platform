from settings import settings
import httpx
from datetime import datetime

from app.db import SessionLocal
from app.models import Metric
from app import owen_token_store

PARAMETER_ID = settings.OWEN_PARAMETER_ID


async def poll_external_api():

    token = owen_token_store.get()
    if not token:
        print("Owen token unavailable; complete POST /login in the app first.")
        return

    async with httpx.AsyncClient() as client:

        # Запрос параметра
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
                device_id=str(PARAMETER_ID),
                name="Общая выручка",
                code="f88",
                value=value,
                timestamp=datetime.utcnow()
            )

            db.add(metric)
            db.commit()

        finally:
            db.close()