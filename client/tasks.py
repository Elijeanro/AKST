from celery import shared_task
from django.utils import timezone
from client.models import Billet
import os
from django.conf import settings

# Définir le nom du projet Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GESTION_DE_BILLET_beta2.settings')

# Configurer les paramètres de Django
settings.configure()



@shared_task
def update_billets():
    # Récupérer tous les billets à mettre à jour
    billets = Billet.objects.filter(infoligne_id__date_dep__lt=timezone.now(), etat_billet=1)
    
    # Mettre à jour les billets
    for billet in billets:
        billet.etat_billet_id = 4
        billet.save()
