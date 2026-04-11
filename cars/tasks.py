from celery import shared_task
import time

from cars.parser.auto_ria_parser import parse_auto_ria


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
def parse_cars_task(max_price = None):
    print("START PARSING")

    cars = parse_auto_ria(max_price)

    print(f"PARSED: {cars}")

    return cars