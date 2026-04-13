from decimal import Decimal


def map_parsed_car_to_model(data: dict):
    try:
        import re

        # --- TITLE ---
        title_parts = data["title"].split()
        brand = title_parts[0]
        model = title_parts[1] if len(title_parts) > 1 else "Unknown"

        # --- YEAR ---
        year_match = re.search(r"\b(19|20)\d{2}\b", data["title"])
        year = int(year_match.group()) if year_match else 2000

        # --- PRICE ---
        price = Decimal(data.get("price", 0))

        # --- MILEAGE ---
        mileage_raw = data.get("mileage", "")
        mileage = int(re.sub(r"\D", "", mileage_raw)) if mileage_raw else 0

        # --- LINK ---
        link = data.get("link")

        return {
            "brand": brand,
            "model": model,
            "year": year,
            "price": price,
            "mileage": mileage,
            "link": link,
        }

    except Exception as e:
        print("MAPPING ERROR:", e)
        return None