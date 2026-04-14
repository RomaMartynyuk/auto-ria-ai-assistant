def normalize_car_query(params: dict):
    max_price = params.get("max_price")
    min_year = params.get("min_year")

    return {
        "max_price": int(max_price) if max_price else None,
        "min_year": int(min_year) if min_year else None,
    }