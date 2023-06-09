from django.contrib import admin
from .models import InfoLigne,Ligne,Bus,Utilisateur,Etat

admin.site.register(InfoLigne)
admin.site.register(Ligne)
admin.site.register(Bus)
admin.site.register(Utilisateur)
admin.site.register(Etat)