from django.shortcuts import render,HttpResponse,get_list_or_404,get_object_or_404,redirect,HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from . import forms,models
import datetime
from dashboard.models import Compagnie,Ville
from companyman.models import Ligne,InfoLigne,Bus
from .functions import code
from django.db.models.query import QuerySet


lecode=code(8)
ville= Ville.objects.all()
ligne= Ligne.objects.all()
infln= InfoLigne.objects.all()
comp= Compagnie.objects.all()
bus= Bus.objects.all()
dnow= datetime.date.today()
dateheure=datetime.datetime.now()
lesdates=InfoLigne.objects.filter(date_dep__gt=datetime.datetime.now()).values_list('date_dep')

def accueil_view(request):
    context = {
        "ville":ville,
        "ligne": ligne,
        "infln": infln,
        "comp": comp,
        "lesbus": bus,
        "dnow": dnow,
    }
    return render(request,'index.html',context)
    
def suggestionForm(request):
    form=forms.SuggestionForm(request.POST)
    if form.is_valid():
        form.save() 
    context={'form':form,}
    return render(request,'suggestion.html',context)

def reservation1_view(request):
    context={'rdt':lesdates,}
    return render(request,'reservation_etape1.html',context)

def infoligne_view(request,ln_id):
    context={'ln':get_object_or_404(Ligne, pk=ln_id),
             'infln':infln.filter(ligne_id=ln_id),
             }
    return render(request,'infoligne.html',context)

def billet_detail_view(request, billet_id):
    billet = get_object_or_404(models.Billet, pk=billet_id)
    infoln = get_object_or_404(InfoLigne, pk=billet.infoligne_id.pk)
    context = {
        'billet': billet,
        'infoln' : infoln,
        'ligne' : ligne,
        }
    return render(request, 'billet_detail.html', context)

def reservation2_view(request,res_id):
    if request.method == 'POST':
        formulaire = forms.BilletForm(request.POST)
        context={
            'res':get_object_or_404(InfoLigne, pk=res_id),
            'inf':infln.get(pk=res_id),
            'form1':formulaire,
            'lecode':lecode,
            'prix':InfoLigne.objects.filter(id=res_id).values_list('prix',flat=True),
        }
        if formulaire.is_valid():
            donnees = formulaire.cleaned_data
            montant= models.Billet(place=donnees['place'],prix=context['prix'])
            billet = forms.Billet.objects.create(
                nom_clt=donnees['nom_clt'], 
                prenom_clt=donnees['prenom_clt'],
                email_clt=donnees['email_clt'],
                telephone_clt=donnees['telephone_clt'],
                place=donnees['place'],
                code_billet=lecode, # une fonction qui génère un code unique pour chaque billet
                infoligne_id=context['inf'],
                prix=context['prix'],
                montant_billet=montant.produit,
            )
            billet.save()
            return redirect(reverse('client:billet_detail_view',args=[billet.pk]))
    else:
        formulaire = forms.BilletForm()
    context={
            'res':get_object_or_404(InfoLigne, pk=res_id),
            'inf':infln.get(pk=res_id),
            'form1':formulaire,
        }
    return render(request, 'reservation_etape2.html', context)