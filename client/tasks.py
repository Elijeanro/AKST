from celery import shared_task,Celery
from django.utils import timezone
from client.models import Billet
import datetime
from django.core.mail import send_mail

celery=Celery('tasks',broker='redis://localhost:6379/0')

import os

os.environ['DJANGO_SETTINGS_MODULE']="GESTION_DE_BILLET_beta2.settings"

@shared_task
def update_billets():
    # Récupérer tous les billets à mettre à jour
    billets = Billet.objects.filter(infoligne_id__date_dep__lt=timezone.now(), etat_billet=1)
    
    # Mettre à jour les billets
    for billet in billets:
        billet.etat_billet_id = 4
        billet.save()
        
def send_reminder_emails():
    # Récupérer tous les billets dont il reste 2 heures avant le départ
    now = datetime.datetime.now()
    two_hours_before_departure = now + datetime.timedelta(hours=2)
    billets = Billet.objects.filter(departure_time__lte=two_hours_before_departure)

    for billet in billets:
        email = billet.email_clt
        username = billet.nom_clt  

        # Envoyer un e-mail au client
        subject = "Rappel de réservation"
        message = f"Cher {username},\n\nIl vous reste 2 heures avant le départ de votre réservation. Veuillez vous présenter à temps à votre point de départ.\n\nCordialement,\nVotre compagnie de transport"
        sender = "jeanrotchallapro@gmail.com"  
        recipients = [email]

        send_mail(subject, message, sender, recipients)
