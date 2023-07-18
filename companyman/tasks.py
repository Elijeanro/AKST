from celery import shared_task
from django.utils import timezone
from client.models import Billet



@shared_task
def update_billets():
    # Récupérer tous les billets à mettre à jour
    billets = Billet.objects.filter(infoligne_id__date_dep__lt=timezone.now(), etat_billet=1)
    
    # Mettre à jour les billets
    for billet in billets:
        billet.etat_billet_id = 4
        billet.save()
    return "Fait"
