import logging

from celery import shared_task
from django.conf import settings
from django.core.cache import cache

from cars.models import Car
from cars.parser.auto_ria_parser import parse_auto_ria
from cars.parser.mapper import map_parsed_car_to_model

logger = logging.getLogger(__name__)
PARSE_LOCK_TTL = 180


def parse_lock_key(max_price, min_price):
    return f"parse-lock:{max_price}:{min_price}"


def parse_freshness_key(max_price, min_price):
    return f"parse-fresh:{max_price}:{min_price}"


def enqueue_parse_cars(max_price=None, min_price=None):
    if cache.get(parse_freshness_key(max_price, min_price)):
        return None

    lock_key = parse_lock_key(max_price, min_price)
    if not cache.add(lock_key, "queued", timeout=PARSE_LOCK_TTL):
        return None

    try:
        return parse_cars_task.delay(max_price, min_price).id
    except Exception:
        cache.delete(lock_key)
        raise


@shared_task
def parse_cars_task(max_price=None, min_price=None):
    lock_key = parse_lock_key(max_price, min_price)
    saved_count = 0

    try:
        cars_data = parse_auto_ria(max_price=max_price, min_price=min_price)

        for raw_car in cars_data:
            mapped = map_parsed_car_to_model(raw_car)
            if not mapped:
                continue

            Car.objects.update_or_create(
                link=mapped["link"],
                defaults={
                    "brand": mapped["brand"],
                    "model": mapped["model"],
                    "year": mapped["year"],
                    "price": mapped["price"],
                    "mileage": mapped["mileage"],
                },
            )
            saved_count += 1

        cache.delete_pattern("cars:*")
        if cars_data:
            cache.set(
                parse_freshness_key(max_price, min_price),
                "fresh",
                timeout=settings.PARSER_REFRESH_SECONDS,
            )
        logger.info("Saved %s of %s parsed cars", saved_count, len(cars_data))
        return {"status": "saved", "parsed": len(cars_data), "saved": saved_count}
    finally:
        cache.delete(lock_key)
