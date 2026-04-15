import json
from openai import OpenAI
import os

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
You are a car recommendation expert.

Select the 5 best cars from the list based on:
- price
- year
- mileage

Return ONLY JSON in this format:
[
  {{
    "id": 1,
    "reason": "short explanation"
  }}
]

Cars:
{cars}
"""

def get_ai_top_cars(cars):
    compressed = [compress_car(c) for c in cars]

    prompt = build_prompt(compressed)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    return json.loads(content)

def map_ai_response(ai_response, cars):
    car_dict = {car.id: car for car in cars}

    result = []

    for item in ai_response:
        car = car_dict.get(item["id"])
        if car:
            car.reason = item["reason"]
            result.append(car)

    return result