from celery import Celery
from src.core.celery.crons.schedule import beat_schedule
from src.core.config import REDIS_HOST_1, REDIS_PORT

celery_app = Celery(
    __name__,
    broker=f"redis://{REDIS_HOST_1}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST_1}:{REDIS_PORT}/0",
    include=[
        "src.core.celery.tasks.organization",
        "src.core.celery.tasks.video",
    ],
)

celery_app.conf.update(
    beat_schedule=beat_schedule,
)
