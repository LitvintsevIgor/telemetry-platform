import random
from datetime import datetime

from app.db import SessionLocal
from app.models import Metric


def poll_external_api():

    print("Generating telemetry data...")

    db = SessionLocal()

    try:

        metric = Metric(
            device_id="device_1",
            metric="temperature",
            value=random.uniform(20, 30),
            timestamp=datetime.utcnow()
        )

        db.add(metric)
        db.commit()

    finally:
        db.close()