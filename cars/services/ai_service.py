import json
import logging
import os
import re

from django.conf import settings

logger = logging.getLogger(__name__)

def compress_car(car):
    return {
        "id": car.id,
        "brand": car.brand,
        "model": car.model,
        "year": car.year,
        "price": int(car.price),
        "mileage": car.mileage,
    }

def build_prompt(cars):
    return f"""
You are a car expert.

From this list of cars, choose up to 5 best options. Prefer cars close to the
customer's budget, then consider year and mileage. Use only IDs from the list.

Cars:
{cars}

STRICT RULES:
- Return ONLY JSON
- No text outside JSON
- MUST include "id"
- If you don't include id → response is invalid

Format:

[
  {{
    "id": 1,
    "reason": "short reason"
  }}
]
"""


def parse_ai_json(content):
    if not content:
        return []

    cleaned = content.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1)

    result = json.loads(cleaned)
    if not isinstance(result, list):
        raise ValueError("AI response must be a JSON array")
    return result


def get_ai_top_cars(cars):
    if not cars or settings.AI_PROVIDER == "none":
        return []

    compressed = [compress_car(c) for c in cars]
    prompt = build_prompt(compressed)

    try:
        if settings.AI_PROVIDER == "openai":
            from openai import OpenAI

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is not configured")
            client = OpenAI(api_key=api_key, timeout=settings.AI_REQUEST_TIMEOUT)
            response = client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = response.choices[0].message.content

        elif settings.AI_PROVIDER == "openrouter":
            content = ask_openrouter(prompt)

        elif settings.AI_PROVIDER == "ollama":
            content = ask_ollama(prompt)

        else:
            raise ValueError(f"Unsupported AI provider: {settings.AI_PROVIDER}")

        return parse_ai_json(content)

    except Exception:
        logger.exception("AI recommendation failed; using deterministic fallback")
        return []

def map_ai_response(ai_response, cars):
    car_dict = {car.id: car for car in cars}

    result = []
    used_ids = set()

    for item in ai_response:
        if not isinstance(item, dict):
            continue

        try:
            car_id = int(item.get("id"))
        except (TypeError, ValueError):
            continue
        reason = item.get("reason", "")

        if not car_id:
            continue

        car = car_dict.get(car_id)

        if car and car_id not in used_ids:
            car.reason = reason
            result.append(car)
            used_ids.add(car_id)

    # Fallback: keep response stable with up to 5 items even when AI
    # returns invalid/short JSON.
    for car in cars:
        if len(result) >= 5:
            break
        if car.id in used_ids:
            continue
        car.reason = getattr(car, "reason", "") or "Selected by fallback ranking."
        result.append(car)
        used_ids.add(car.id)

    return result

def ask_ollama(prompt: str) -> str:
    import requests

    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    response = requests.post(
        f"{ollama_base_url.rstrip('/')}/api/generate",
        json={
            "model": settings.AI_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=settings.AI_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get("response", "")

def ask_openrouter(prompt: str) -> str:
    import requests

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not configured")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.AI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=settings.AI_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
