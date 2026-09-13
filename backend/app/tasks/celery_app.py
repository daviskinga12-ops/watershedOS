import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "watershedos",
    broker=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "pull-satellite-data-every-5-days": {
        "task": "app.tasks.scheduled_pull.run_pipeline",
        "schedule": 5 * 24 * 60 * 60,  # every 5 days, in seconds
    },
    "check-restoration-ndvi-daily": {
        "task": "app.tasks.scheduled_pull.check_restoration_ndvi",
        "schedule": 24 * 60 * 60,
    },
    "purge-expired-personal-data-weekly": {
        "task": "app.tasks.retention.purge_expired_personal_data",
        "schedule": 7 * 24 * 60 * 60,
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
