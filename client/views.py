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
etat=models.EtatBillet.objects.all()
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
        form=forms.SuggestionForm() 
    context={'form':form,}
    return render(request,'suggestion.html',context)

def reservation1_view(request):
    context={'rdt':lesdates,}
    return render(request,'reservation_etape1.html',context)


def listechoix_view(request):
    context={'rdt':lesdates,
             'infln':infln,
             'lignes':ligne,}
    return render(request,'listechoix.html',context)


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
                bl_valide=True,
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

# def annulation1_view(request):
#     if request.method=='POST':
#         recherche=forms.RechercheBillet(request.POST)
#         billet=models.Billet.objects.all()
#         if recherche.is_valid():
#             donnee=recherche.cleaned_data
#             code=donnee['code_billet']
#             resultat=billet.filter(code_billet=code)
#             if resultat is not None:
#                 idbillet=billet.filter(code_billet=code).values_list('id',flat=True)
#                 return redirect(reverse('client:annulation2',args=idbillet))
#             else:
#                 message="Aucun billet ne correspond à ce code"
#                 return HttpResponse(render,message)
#     else:
#         recherche=forms.RechercheBillet()
#         context={
#             'recherche':recherche,
#         }
#     return render(request,'annulation1.html',context)

# def annulation2_view(request, billet_id):
#     billet = get_object_or_404(models.Billet, pk=billet_id)
#     infoln = get_object_or_404(InfoLigne, pk=billet.infoligne_id.pk)
#     context = {
#         'billet': billet,
#         'infoln' : infoln,
#         'ligne' : ligne,
#         }
#     return render(request, 'billet_detail.html', context)

def recherche1_view(request):
    if request.method == 'POST':
        recherche = forms.RechercheBillet(request.POST)
        if recherche.is_valid():
            donnees = recherche.cleaned_data
            code = donnees['code_billet']
            resultat = models.Billet.objects.filter(code_billet=code).first()
            if resultat is not None:
                id_billet = resultat.id
                return redirect(reverse('client:annulation2', args=[id_billet]))
            else:
                message = "Aucun billet ne correspond à ce code"
                return HttpResponse(message)
    else:
        recherche = forms.RechercheBillet()
    context = {
        'recherche': recherche,
    }
    return render(request, 'annulation1.html', context)

def annulation_view(request, billet_id):
    billet = get_object_or_404(models.Billet, id=billet_id)
    infoln = get_object_or_404(models.InfoLigne, id=billet.infoligne_id.id)
    etatb=get_object_or_404(models.EtatBillet, id=billet.etat_billet.id)
    context = {
        'billet': billet,
        'infoln': infoln,
        'ligne': ligne,
        'etat':etatb,
    }
    
    return render(request, 'annulation2.html', context)

def annuler_billet(request, billet_id):
    billet = get_object_or_404(models.Billet, id=billet_id)
    billet.etat_billet = models.EtatBillet.objects.get(id=3)
    billet.bl_valide = False
    billet.save()

    return redirect('client:billet_detail_view', billet_id=billet.id)


def recherche2_view(request):
    if request.method == 'POST':
        recherche = forms.RechercheBillet(request.POST)
        if recherche.is_valid():
            donnees = recherche.cleaned_data
            code = donnees['code_billet']
            resultat = models.Billet.objects.filter(code_billet=code).first()
            if resultat is not None:
                id_billet = resultat.id
                return redirect(reverse('client:modification2', args=[id_billet]))
            else:
                message = "Aucun billet ne correspond à ce code"
                return HttpResponse(message)
    else:
        recherche = forms.RechercheBillet()
    context = {
        'recherche': recherche,
    }
    return render(request, 'modification1.html', context)

def modifier_billet(request, billet_id):
    billet = get_object_or_404(models.Billet, id=billet_id)

    if request.method == 'POST':
        form = forms.BilletForm(request.POST, instance=billet)
        if form.is_valid():
            form.save()
            return redirect('client:billet_detail_view', billet_id=billet.id)
    else:
        form = forms.BilletForm()

    context = {
        'form': form,
        'billet': billet
    }
    return render(request, 'modification2.html', context)

def lescompagnies_view(request):
    context={
        'comp':comp,
             }
    return render(request,'lescompagnies.html',context)

def lacompagnie_view(request,cp_id):
    context={
        'cp':get_object_or_404(Compagnie, pk=cp_id),
             }
    return render(request,'lacompagnie.html',context)
