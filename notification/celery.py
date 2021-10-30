import os
from celery import Celery
os.environ.setdefaut('DJANGO_SETTING_MODULE','notification.settings')
app = Celery('notification')
app.config.from_object('django.conf.settings',namespace='CELERY')
app.autodiscover_tasks()
