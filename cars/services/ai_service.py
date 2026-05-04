import json
from openai import OpenAI
import os
import requests
from django.conf import settings

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

From this list of cars, choose the best 5 options.

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

def get_ai_top_cars(cars):
    compressed = [compress_car(c) for c in cars]
    prompt = build_prompt(compressed)

    provider = getattr(settings, "AI_PROVIDER", "openai")

    try:
        if provider == "openai":
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content

        elif provider == "openrouter":
            content = ask_openrouter(prompt)

        elif provider == "ollama":
            content = ask_ollama(prompt)

        else:
            raise ValueError("Invalid AI provider")

        return json.loads(content)

    except Exception as e:
        print("AI ERROR:", e)
        return []

    return json.loads(content)

def map_ai_response(ai_response, cars):
    car_dict = {car.id: car for car in cars}

    result = []
    used_ids = set()

    for item in ai_response:
        car_id = item.get("id")
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
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        response = requests.post(
            f"{ollama_base_url}/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json().get("response", "")

    except Exception as e:
        print("OLLAMA ERROR:", e)
        return ""



def ask_openrouter(prompt: str) -> str:
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            },
        )

        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print("OPENROUTER ERROR:", e)
        return ""
