from django import forms
from .models import Suggestion,Billet
from companyman.models import InfoLigne
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .functions import liste_infoligne,liste_ville
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
import phonenumbers
import datetime


destinataires=[
    ('Plateforme','La Plateforme'),
    ('Nagode', 'Compagnie Nagode'),
    ('Cheval Blanc', 'Compagnie Cheval Blanc'),
    ('Rakieta', 'Compagnie Rakieta'),
    ('LK', 'Compagnie LK'),
    ('ETRAB', 'Compagnie ETRAB'),
    ('Adji Transport', 'Compagnie Adji Transport'),
    ('DC10', 'Compagnie DC10')
]


class SuggestionForm(forms.ModelForm):
    class Meta:
        model=Suggestion
        fields=('email','destinataire','message')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input100', 'placeholder':'Email'}),
            'destinataire': forms.Select(attrs={'class': 'input100', 'placeholder':'Destiné à'}, choices=destinataires), 
            'message': forms.Textarea(attrs={'class': 'input100', 'placeholder':'Saisissez Votre Message...'}),
        }

class BilletForm(forms.Form):
    nom_clt=forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input100', 'placeholder':'Nom'})
        )
    prenom_clt=forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input100', 'placeholder':'Prénom'})
        )
    email_clt=forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input100', 'placeholder':'E-mail'})
        )
    telephone_clt=PhoneNumberField(
        widget=PhoneNumberPrefixWidget(attrs={'class': 'input100', 'placeholder':'Téléphone'})
        )
    place=forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'input20',
            'min':'1', 
            'max':'5',
            'placeholder':'Place'})
        )
    
class ContactForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Envoyer'))

        self.helper.layout = Layout(
            'email',
            'message',
        )
class RechercheBillet(forms.Form):
    code_billet=forms.CharField(widget=forms.TextInput(attrs={'class': 'input100', 'placeholder':'Code'})
        )        
    