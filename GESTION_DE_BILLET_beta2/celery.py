from celery import Celery
from datetime import timedelta
from django.utils import timezone
from client.models import Billet

# Créer une instance de l'application Celery
app = Celery('GESTION_DE_BILLET_beta2')

# Charger la configuration de Django pour Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir les tâches dans les applications Django
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from client.tasks import update_billets
    # Planifier la tâche pour s'exécuter toutes les 60 secondes
    sender.add_periodic_task(60.0, update_billets.s(), name='update-billets')


@app.task
def update_billets():
    # Récupérer tous les billets à mettre à jour
    billets = Billet.objects.filter(infoligne_id__date_dep__lt=timezone.now(), etat_billet=1)
    
    # Mettre à jour les billets
    for billet in billets:
        billet.etat_billet_id = 4
        billet.save()
