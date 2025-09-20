from celery import Celery
from src.config import settings

app = Celery(
    "quotes",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.tasks.refresh_quotes"],
)

app.conf.beat_schedule = {
    "refresh-quotes-every-5-mins": {
        "task": "refresh_quotes",
        "schedule": 300,  # 300s = 5 minutos
    },
}