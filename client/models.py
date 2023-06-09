from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from dashboard.models import Compagnie
from companyman.models import InfoLigne
from django.urls import reverse
from django.db.models.query import QuerySet
from django.utils import timezone

class Suggestion(models.Model):
    email=models.CharField(max_length=20)
    destinataire=models.CharField(max_length=30, default='Plateforme')
    message=models.TextField(max_length=500)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.date
    
class EtatBillet(models.Model):
        libelle=models.CharField(max_length=20)
class Billet(models.Model):
    nom_clt = models.CharField(max_length=30)
    prenom_clt = models.CharField(max_length=50)
    email_clt = models.CharField(max_length=60, blank=True, null=True)
    telephone_clt = PhoneNumberField(region='TG', blank=True, null=True)
    code_billet = models.CharField(max_length=12)
    infoligne_id = models.ForeignKey(InfoLigne, on_delete=models.DO_NOTHING)
    prix = models.FloatField()
    place = models.SmallIntegerField()
    montant_billet = models.FloatField()
    date_heure = models.DateTimeField(auto_now_add=True)
    etat_billet = models.ForeignKey(EtatBillet, on_delete=models.DO_NOTHING, default=1)
    bl_valide = models.BooleanField(default=True)
    id_paiement = models.CharField(max_length=512, null=True)

    def __str__(self):
        return str(self.code_billet)

    def save(self, *args, **kwargs):
        if self.etat_billet_id == 1 and self.infoligne_id.date_dep < timezone.now():
            self.etat_billet_id = 4
        super().save(*args, **kwargs)

    @property
    def produit(self):
        prix_unitaire = self.prix.first() if isinstance(self.prix, QuerySet) else self.prix
        return self.place * prix_unitaire
