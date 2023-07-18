from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Compagnie(models.Model):
    nom_cp=models.CharField(max_length=15)
    telephone_cp=PhoneNumberField(region='TG', 
        blank=True, 
        null=True, 
        )
    email_cp=models.EmailField(blank=True,null=True)
    siege_cp=models.CharField(max_length=100)
    
class Grade(models.Model):
    libelle_grd=models.CharField(max_length=20)
    def __str__(self):
        return self.libelle_grd
    
class Ville(models.Model):
    nom_ville=models.CharField(max_length=100)
    def __str__(self):
        return self.nom_ville