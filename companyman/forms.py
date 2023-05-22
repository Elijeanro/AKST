from .models import Ligne,InfoLigne,Utilisateur,Grade
from django import forms
from django.forms import ModelChoiceField, ModelForm
from client.models import Billet
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

lignes=Ligne.objects.all()
leslignes=[]
for i in lignes:
    leslignes.append((i.id,i.libelle))

grades=Grade.objects.all()
lesgrades=[]
for i in grades:
    lesgrades.append((i.id,i.libelle_grd))

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
    grade_id = forms.ModelChoiceField(queryset=Grade.objects.all().values_list('libelle_grd',flat=True), widget=forms.Select(attrs={'class':'form-control form-control-user', 'placeholder':'Grade'}))
    nom_user = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-user', 'placeholder':'Nom'}))
    prenom_user = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-user', 'placeholder':'Prénom'}))
    email_user = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control form-control-user', 'placeholder':'Email'}))
    nom_utilisateur = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-control-user', 'placeholder':"Nom d'utilisateur"}))
    pw_user = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-user', 'placeholder':'Mot de passe'}))

    class Meta:
        model = Utilisateur
        fields = ('grade_id', 'nom_user', 'prenom_user', 'email_user', 'nom_utilisateur', 'pw_user')

    