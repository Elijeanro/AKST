from .models import Ligne, InfoLigne, Utilisateur, Grade, Bus
from dashboard.models import Ville, Compagnie
from django import forms
from django.forms import ModelChoiceField, ModelForm, DateTimeInput
from client.models import Billet
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class CustomDateTimeInput(DateTimeInput):
    def __init__(self, attrs=None, format=None):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'form-control datetimepicker'
        attrs['placeholder'] = 'Date de départ'
        super().__init__(attrs=attrs, format=format)



class BusForm(forms.Form):
    matricule_bus = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matricule'}))
    nb_place = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de place'}))

class RechercherBus(forms.Form):
    matricule_bus = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Saisir le Code du billet'}))

class RechercheBillet(forms.Form):
    code_billet = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Saisir le Code du billet'}))

class RechercherUtilisateur(forms.Form):
    nom_utilisateur = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Enter Username...'}))
    pw_user = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Password'}))

class RechercherUtilisateur2(forms.Form):
    nom_user = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Enter Name...'}))
    prenom_user = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Enter Firstname...'}))
    email_user = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Enter Email address...'}))
    nom_utilisateur = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Enter Username...'}))
    pw_user = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Enter Password...'}))
    
class InfoligneForm(forms.ModelForm):
    bus_id = forms.ModelChoiceField(queryset=Bus.objects.none(), widget=forms.Select(attrs={'class': 'form-control form-control', 'placeholder': 'Bus'}), empty_label=None, to_field_name='matricule_bus')
    ligne_id = forms.ModelChoiceField(queryset=Ligne.objects.all(), widget=forms.Select(attrs={'class': 'form-control form-control', 'placeholder': 'Ligne'}), empty_label=None, to_field_name='id')
    date_dep = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control datetimepicker', 'placeholder': 'Date de départ'}),
        input_formats=['%Y-%m-%d %H:%M:%S']
    )
    
    class Meta:
        model = InfoLigne
        fields = ('date_dep', 'prix', 'bus_id', 'ligne_id', 'place_restante')
        widgets = {
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix'}),
            'place_restante': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Place restante'}),
        }

    def __init__(self, *args, **kwargs):
        compagnie_id = kwargs.pop('compagnie_id', None)
        super().__init__(*args, **kwargs)
        if compagnie_id:
            self.fields['bus_id'].queryset = Bus.objects.filter(etat_bus=2, compagnie_id=compagnie_id)

class UtilisateurForm(forms.ModelForm):
    grade_id = forms.ModelChoiceField(queryset=Grade.objects.filter(id__in=[2, 3]), widget=forms.Select(attrs={'class': 'form-control form-control', 'placeholder': 'Grade'}), empty_label=None, to_field_name='libelle_grd')
    personnel_actif = forms.BooleanField(widget=forms.HiddenInput(), initial=True)  # Champ personnel_actif

    class Meta:
        model = Utilisateur
        fields = ('grade_id', 'nom_user', 'prenom_user', 'email_user', 'nom_utilisateur', 'pw_user', 'personnel_actif')  
        widgets = {
            'nom_user': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom_user': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'email_user': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'nom_utilisateur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
            'pw_user': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
        }
