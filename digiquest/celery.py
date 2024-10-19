from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digiquest.settings')
app = Celery('digiquest')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['doctorappointment'])  # This should match the name of your app

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')



