ALLOWED_ORDERING_FIELDS = {"price", "-price", "year", "-year", "mileage", "-mileage"}


def _positive_int(params, name):
    value = params.get(name)
    if value in (None, ""):
        return None

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc

    if parsed <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return parsed


def normalize_car_query(params):
    ordering = params.get("ordering") or None
    if ordering and ordering not in ALLOWED_ORDERING_FIELDS:
        raise ValueError(
            "ordering must be one of: " + ", ".join(sorted(ALLOWED_ORDERING_FIELDS))
        )

    brand = (params.get("brand") or "").strip() or None

    return {
        "max_price": _positive_int(params, "max_price"),
        "min_year": _positive_int(params, "min_year"),
        "max_mileage": _positive_int(params, "max_mileage"),
        "brand": brand,
        "ordering": ordering,
    }
