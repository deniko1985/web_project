import os
import time

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_CLI = os.getenv("REDIS_CLI")


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", REDIS_CLI)


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True
