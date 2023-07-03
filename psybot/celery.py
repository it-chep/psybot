import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psybot.settings')

app = Celery('telegrambot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# app2 = Celery('users')
# app2.config_from_object('django.conf:settings', namespace='CELERY')
# app2.autodiscover_tasks()

