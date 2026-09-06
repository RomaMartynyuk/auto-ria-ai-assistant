import logging

from django.conf import settings
from django.core.cache import cache

from cars.models import Car

logger = logging.getLogger(__name__)


def recommendation_price_floor(max_price):
    if not max_price:
        return None
    return int(max_price * settings.RECOMMENDATION_MIN_BUDGET_RATIO)


def filter_cars(
    max_price=None,
    min_price=None,
    min_year=None,
    max_mileage=None,
    brand=None,
    ordering=None,
):
    cache_key = (
        f"cars:{max_price}:{min_price}:{min_year}:{max_mileage}:{brand}:{ordering}"
    )

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        logger.info("FROM CACHE")
        return cached_data

    logger.info("FROM DB")

    cars = Car.objects.all()

    if max_price:
        cars = cars.filter(price__lte=max_price)

    if min_price:
        cars = cars.filter(price__gte=min_price)

    if min_year:
        cars = cars.filter(year__gte=min_year)

    if max_mileage:
        cars = cars.filter(mileage__lte=max_mileage)

    if brand:
        cars = cars.filter(brand__icontains=brand)

    if ordering:
        cars = cars.order_by(ordering)
    else:
        cars = cars.order_by("-year")

    cars = list(cars)

    cache.set(cache_key, cars, timeout=60 * 5)

    return cars
