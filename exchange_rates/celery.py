import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exchange_rates.settings")

app = Celery("exchange_rates")
every_3_am = crontab(minute=0, hour=3)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "mono-USD-UAH": {
        "task": "exchange.tasks.start_exchange",
        "schedule": every_3_am,
        "args": ("mono", "USD", "UAH"),
    },
    "mono-EUR-UAH": {
        "task": "exchange.tasks.start_exchange",
        "schedule": every_3_am,
        "args": ("mono", "EUR", "UAH"),
    },
    "privat-EUR-UAH": {
        "task": "exchange.tasks.start_exchange",
        "schedule": every_3_am,
        "args": ("privat", "EUR", "UAH"),
    },
    "privat-USD-UAH": {
        "task": "exchange.tasks.start_exchange",
        "schedule": every_3_am,
        "args": ("privat", "USD", "UAH"),
    },
}
