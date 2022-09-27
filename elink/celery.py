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
    "optimize_live_time_cache": {
        "task": "service.tasks.optimize_live_time_cache",
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
    # Оптимизируем обращение к панели(например юзер зайдет в первый раз а у него 1м+ записей и сайт подвиснет),
    # модуль порционно записывает данные в фоновом процессе, только если их много
    "optimize_panel":{
        "task": "service.tasks.optimize_panel",
        "schedule": crontab(minute="*/15"),  # В 00:30 по Мск
    },
}
app.conf.timezone = "UTC"
