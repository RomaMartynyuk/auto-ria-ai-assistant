from celery import shared_task
import time

@shared_task
def test_task():
    print("Testing task")
    time.sleep(5)
    print("Task executed")

    return "done"