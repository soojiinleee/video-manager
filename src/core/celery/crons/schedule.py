from celery.schedules import crontab

beat_schedule = {
    "expire-paid-subscriptions-daily": {
        "task": "expire_paid_subscriptions",
        "schedule": crontab(minute=0, hour=9),  # UTC 기준 매일 자정 실행
    }
}
