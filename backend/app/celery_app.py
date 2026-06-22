import os
from celery import Celery
from celery.schedules import crontab

# Broker and Backend URL from environment variable
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "voicera",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BROKER_URL,
    include=["app.tasks.booking_tasks"]
)

celery_app.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    beat_schedule={
        "check_no_shows": {
            "task": "app.tasks.booking_tasks.check_no_shows",
            "schedule": crontab(minute="*/5"),
        },
        "send_reminders": {
            "task": "app.tasks.booking_tasks.send_reminders",
            "schedule": crontab(minute="*/10"),
        },
    }
)

if __name__ == "__main__":
    celery_app.start()
