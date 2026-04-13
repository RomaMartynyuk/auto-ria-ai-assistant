from celery import shared_task
from django.core.cache import cache
import time

from cars.models import Car
from cars.parser.auto_ria_parser import parse_auto_ria
from cars.parser.mapper import map_parsed_car_to_model


@shared_task
def test_task():
    print("Testing task")
    time.sleep(5)
    print("Task executed")

    return "done"

@shared_task
def process_car_search(max_price, min_year):
    print("START PARSING / PROCESSING")

    time.sleep(5)

    print(f"Filters: price={max_price}, year={min_year}")

    print("END TASK")

    return {"status": "done"}

@shared_task
def parse_cars_task(max_price=None):
    cars_data = parse_auto_ria(max_price)

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
            }
        )

    cache.clear()

    return {"status": "saved"}