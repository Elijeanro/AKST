from .models import Ligne,InfoLigne,Utilisateur
from django import forms
from client.models import Billet
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

lignes=Ligne.objects.all()
leslignes=[]
for i in lignes:
    leslignes.append((i.id,i.libelle))

class BusForm(forms.Form):
    matricule_bus=forms.CharField(widget=forms.TextInput)
    nb_place=forms.IntegerField(widget=forms.NumberInput)
    
class RechercheBillet(forms.Form):
    code_billet=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-user', 'placeholder':'Saisir le Code du billet'})
        ) 

class RechercherUtilisateur(forms.Form):
    nom_utilisateur=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-user', 'placeholder':'Enter Username...'}))
    pw_user=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-user', 'placeholder':'Password'}))
    
class InfoligneForm(forms.ModelForm):
    class Meta:
        model=InfoLigne
        fields=('date_dep','ligne_id','prix','bus_id')
        widgets={
            'date_dep':forms.DateTimeField,
            'ligne_id':forms.Select(choices=leslignes),
            'prix':forms.DecimalField,
            'bus_id':forms.Select()
        }
        
class UtilisateurForm(forms.ModelForm):
    class Meta:
        model=Utilisateur
        fields=('grade_id','nom_user','prenom_user','email_user','nom_utilisateur','pw_user')
    