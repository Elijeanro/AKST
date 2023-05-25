from django.db import models
from dashboard.models import Compagnie,Grade,Ville

class Bus(models.Model):
    matricule_bus=models.CharField(max_length=12)
    nb_place=models.PositiveSmallIntegerField(default=0)
    compagnie_id=models.ForeignKey(Compagnie, on_delete=models.DO_NOTHING)
    
    
class Ligne(models.Model):
    libelle=models.CharField(max_length=40, null=True)
    ville_dep=models.ForeignKey(Ville,on_delete=models.DO_NOTHING,related_name='depart' )
    ville_arr=models.ForeignKey(Ville,on_delete=models.DO_NOTHING,related_name='arrivee' )
    duree_trajet=models.DurationField(null=True)
    
    
class InfoLigne(models.Model):
    date_dep=models.DateTimeField()
    ligne_id=models.ForeignKey(Ligne,on_delete=models.DO_NOTHING)
    prix=models.FloatField(default=0)
    bus_id=models.ForeignKey(Bus, on_delete=models.DO_NOTHING) 
    place_restante=models.PositiveSmallIntegerField(default=60)
    position=models.ForeignKey(Ville, on_delete=models.DO_NOTHING, default=1)
   
class Utilisateur(models.Model):
    grade_id=models.ForeignKey(Grade, on_delete=models.DO_NOTHING)
    nom_user=models.CharField(max_length=30)
    prenom_user=models.CharField(max_length=50)
    email_user=models.CharField(max_length=60)
    nom_utilisateur=models.CharField(max_length=10)
    pw_user=models.CharField(max_length=12)
    compagnie_id=models.ForeignKey(Compagnie, on_delete=models.DO_NOTHING)