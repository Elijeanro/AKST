from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from datetime import timedelta
from celery.schedules import crontab

# Définir le nom du projet Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GESTION_DE_BILLET_beta2.settings')

app = Celery('GESTION_DE_BILLET_beta2')
app.conf.result_serializer = 'json'
# Charger la configuration de Celery à partir des paramètres Django
app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    'update-billets-every-minute': {
        'task': 'companyman/tasks.update_billets',
        'schedule': timedelta(minutes=1),
    },
}

# Découvrir les tâches automatiques dans les applications Django
app.autodiscover_tasks()

app.task(bind=True)

def debug_task(self):
    print(f'Request : {self.request!r}')