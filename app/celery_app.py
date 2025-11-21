# from celery import Celery
# from app.config import settings


# celery_app = Celery(
#     "worker",
#     broker=settings.REDIS_URL,      # from .env
#     backend=settings.REDIS_URL,     # Redis backend (optional but OK)
#     include=["app.tasks"]           # your tasks.py
# )

# # Auto-discover tasks inside app/ if you add more later
# celery_app.autodiscover_tasks(["app"])

# # Celery Beat schedule
# celery_app.conf.beat_schedule = {
#     "scan-every-10-seconds": {
#         "task": "scan_for_violations",
#         "schedule": 10.0,
#     },
# }

# celery_app.conf.timezone = "UTC"


from celery import Celery
from app.config import settings

celery_app = Celery(
    "airguardian",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

celery_app.conf.beat_schedule = {
    "scan-every-10-seconds": {
        "task": "scan_for_violations",
        "schedule": 10.0,
    }
}

celery_app.conf.timezone = "UTC"
