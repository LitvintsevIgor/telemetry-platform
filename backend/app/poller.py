import re
from datetime import datetime

import httpx

from settings import settings
from app.db import SessionLocal
from app.models import Metric
from app import owen_token_store

OWEN_API_BASE = "https://api.owencloud.ru"
_CODE_PATTERN = re.compile(r"^([a-zA-Z])(\d+)$")


def parse_parameter_code(code: str) -> tuple[int, str] | None:
    if not code or not isinstance(code, str):
        return None
    m = _CODE_PATTERN.match(code.strip())
    if not m:
        print(f"owen poll: skip parameter, invalid code format: {code!r}")
        return None
    letter = m.group(1).lower()
    if letter not in ("a", "b"):
        print(f"owen poll: skip parameter, unknown payment letter in code {code!r}")
        return None
    box_id = int(m.group(2))
    payment_type = "cash" if letter == "a" else "card"
    return (box_id, payment_type)


def _coerce_value(raw) -> float | None:
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        print(f"owen poll: skip parameter, non-numeric value: {raw!r}")
        return None


def _extract_parameters(payload) -> list:
    if not isinstance(payload, dict):
        return []
    params = payload.get("parameters")
    if isinstance(params, list):
        return params
    return []


async def poll_external_api():
    token = owen_token_store.get()
    if not token:
        print("Owen token unavailable; complete POST /login in the app first.")
        return

    url = f"{OWEN_API_BASE}/v1/device/{settings.OWEN_DEVICE_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "*/*",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=[])

    try:
        payload = response.json()
    except Exception:
        print("owen poll: invalid JSON response:", response.text[:500])
        return

    if response.status_code != 200:
        print(
            "owen poll: device request failed:",
            response.status_code,
            response.text[:500],
        )
        return

    rows: list[Metric] = []
    ts = datetime.utcnow()

    for item in _extract_parameters(payload):
        if not isinstance(item, dict):
            continue
        code = item.get("code")
        if code is None:
            print("owen poll: skip parameter, missing code")
            continue
        parsed = parse_parameter_code(str(code))
        if parsed is None:
            continue
        box_id, payment_type = parsed
        val = _coerce_value(item.get("value"))
        if val is None:
            continue
        rows.append(
            Metric(
                timestamp=ts,
                box_id=box_id,
                payment_type=payment_type,
                value=val,
            )
        )

    if not rows:
        print("owen poll: no parameter rows to store")
        return

    db = SessionLocal()
    try:
        db.add_all(rows)
        db.commit()
    finally:
        db.close()
