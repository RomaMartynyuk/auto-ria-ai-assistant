import re
from decimal import Decimal, InvalidOperation


def parse_mileage(value):
    if not value:
        return 0

    normalized = str(value).lower().replace(",", ".").replace("\u00a0", " ")
    match = re.search(r"\d+(?:\.\d+)?", normalized)
    if not match:
        return 0

    mileage = float(match.group())
    if "тис" in normalized or "thousand" in normalized:
        mileage *= 1000
    return int(mileage)


def map_parsed_car_to_model(data: dict):
    try:
        title = data["title"].strip()
        title_parts = title.split()
        brand = data.get("brand") or title_parts[0]
        model = data.get("model") or (
            title_parts[1] if len(title_parts) > 1 else "Unknown"
        )

        year_match = re.search(r"\b(19|20)\d{2}\b", title)
        year = int(data.get("year") or (year_match.group() if year_match else 2000))
        price = Decimal(data.get("price", 0))
        if price <= 0:
            return None

        mileage = parse_mileage(data.get("mileage"))
        link = data.get("link")
        if not link:
            return None

        return {
            "brand": brand,
            "model": model,
            "year": year,
            "price": price,
            "mileage": mileage,
            "link": link,
        }

    except (KeyError, TypeError, ValueError, InvalidOperation):
        return None
