def normalize_car_query(params: dict):
    max_price = params.get("max_price")
    min_year = params.get("min_year")
    max_mileage = params.get("max_mileage")
    brand = params.get("brand")
    ordering = params.get("ordering")

    return {
        "max_price": int(max_price) if max_price else None,
        "min_year": int(min_year) if min_year else None,
        "max_mileage": int(max_mileage) if max_mileage else None,
        "brand": str(brand) if brand else None,
        "ordering": str(ordering) if ordering else None,
    }