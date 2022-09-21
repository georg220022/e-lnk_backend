import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elink.settings")

app = Celery("elink")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "saver_info": {
        "task": "service.tasks.saver_info",
        "schedule": crontab(minute="0", hour="*/1"),  # Каждый час
    },
    # Каждую минуту проверяет нагрузку на ЦП, увеличивая время жизни кеша при большой нагрузке
    "optimize_live_time_cache": {
        "task": "service.tasks.optimize_live_time_cache",
        "schedule": crontab(),
    },
    # Отправка полной статистики в telegram администраторам
    "send_admin_stat_tg": {
        "task": "service.tasks.send_admin_stat_tg",
        "schedule": crontab(minute=0, hour=21),  # Ежедневно в полночь по Мск
    },
    # Очищаем устаревшие данные, записи о токенах
    "cleaner_db": {
        "task": "service.tasks.cleaner_db",
        "schedule": crontab(minute=30, hour=21),  # В 00:30 по Мск
    },
}
app.conf.timezone = "UTC"
