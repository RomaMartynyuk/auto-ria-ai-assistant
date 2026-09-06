import os

import httpx

BASE_URL = os.getenv("API_BASE_URL", "http://web:8000/api").rstrip("/")
API_TIMEOUT = float(os.getenv("BOT_API_TIMEOUT", "60"))


async def get_cars(params: dict):
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/recommend/", params=params)

        if response.status_code == 200:
            return {"status": "ready", "cars": response.json()}

        if response.status_code == 202:
            return response.json()

        detail = response.json().get("error", response.text)
        return {"status": "error", "message": detail}

    except (httpx.RequestError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}
