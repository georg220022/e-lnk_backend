import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elink.settings')
app = Celery('elink')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'update_week_stat': {
        'task': 'personal_area.tasks.updater_week_stat',
        'schedule': crontab(minute='*/1')
    },
}
app.conf.timezone = 'UTC'
