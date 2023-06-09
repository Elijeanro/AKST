from django.db import models
from dashboard.models import Compagnie, Grade, Ville
from datetime import datetime, timedelta
from django.urls import reverse

class Etat(models.Model):
    libelle= models.CharField(max_length=30)
    def __str__(self):
        return self.libelle

class Bus(models.Model):
    matricule_bus = models.CharField(max_length=12)
    nb_place = models.PositiveSmallIntegerField(default=0)
    compagnie_id = models.ForeignKey(Compagnie, on_delete=models.CASCADE)
    etat_bus = models.ForeignKey(Etat, on_delete=models.DO_NOTHING, default=2)
    def __str__(self):
        return self.matricule_bus


class Ligne(models.Model):
    libelle = models.CharField(max_length=40, null=True)
    ville_dep = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='depart')
    ville_arr = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='arrivee')
    duree_trajet = models.DurationField(null=True)

    def __str__(self):
        return self.libelle

    def get_duree_trajet_str(self):
        hours, minutes, seconds = self.duree_trajet.total_seconds() // 3600, (self.duree_trajet.total_seconds() % 3600) // 60, self.duree_trajet.total_seconds() % 60
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

class InfoLigne(models.Model):
    date_dep=models.DateTimeField()
    date_arr=models.DateTimeField(null=True)
    ligne_id=models.ForeignKey(Ligne,on_delete=models.DO_NOTHING)
    prix=models.FloatField(default=0)
    bus_id=models.ForeignKey(Bus, on_delete=models.DO_NOTHING, default=1) 
    place_restante=models.PositiveSmallIntegerField(default=60)
    position=models.ForeignKey(Ville, on_delete=models.DO_NOTHING, default=1)
    etat_infoligne = models.ForeignKey(Etat, on_delete=models.DO_NOTHING, default=2)
    def get_absolute_url(self):
        return reverse('nom_de_la_vue', args=[self.id])
    def __str__(self):
        return f"InfoLigne (date_dep={self.date_dep.strftime('%Y-%m-%d %H:%M:%S')}, date_arr={self.date_arr.strftime('%Y-%m-%d %H:%M:%S')}, ...)"


class Utilisateur(models.Model):
    grade_id = models.ForeignKey(Grade, on_delete=models.CASCADE)
    nom_user = models.CharField(max_length=30)
    prenom_user = models.CharField(max_length=50)
    email_user = models.CharField(max_length=60)
    nom_utilisateur = models.CharField(max_length=10)
    pw_user = models.CharField(max_length=12)
    compagnie_id = models.ForeignKey(Compagnie, on_delete=models.CASCADE)
    personnel_actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom_user
