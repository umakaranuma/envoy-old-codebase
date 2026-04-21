import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envoy_bu_policy_api.settings')

app = Celery('envoy_bu_policy_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')