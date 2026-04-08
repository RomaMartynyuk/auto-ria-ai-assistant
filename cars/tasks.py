from celery import shared_task
import time

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