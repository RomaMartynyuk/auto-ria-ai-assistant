from cars.models import Car
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def filter_cars(max_price=None, min_year=None):
    cache_key = f"cars_{max_price}_{min_year}"

    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info("FROM CACHE")
        return cached_data

    logger.info("FROM DB")

    cars = Car.objects.all()

    if max_price:
        cars = cars.filter(price__lte=max_price)

    if min_year:
        cars = cars.filter(year__gte=min_year)

    cars = list(cars)

    cache.set(cache_key, cars, timeout=60 * 5)

    return cars