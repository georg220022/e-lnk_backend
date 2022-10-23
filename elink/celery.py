import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elink.settings")

app = Celery("elink")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    # Сохраняем данные о кликах по ссылкам каждый час одним большим запросом bulk_create
    "saver_info": {
        "task": "service.tasks.saver_info",
        "schedule": crontab(minute="0", hour="*/1"),
    },
    # Каждую минуту проверяет нагрузку на ЦП, увеличивая время жизни кеша при большой нагрузке
    # Так же высчитывает статистику если для некоторого пользователя слишком много кликов
    "optimize_ttl_and_perfomance": {
        "task": "service.tasks.optimize_ttl_and_perfomance",
        "schedule": crontab(),
    },
    # Отправка полной статистики в telegram администраторам
    "send_admin_stat_tg": {
        "task": "service.tasks.send_admin_stat_tg",
        "schedule": crontab(minute=5, hour=21),  # Ежедневно в 00:05 по Мск
    },
    # Очищаем устаревшие данные, записи о токенах
    "cleaner_db": {
        "task": "service.tasks.cleaner_db",
        "schedule": crontab(minute=30, hour=21),  # В 00:30 по Мск
    },
}
app.conf.timezone = "UTC"
