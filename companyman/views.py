from django.shortcuts import render,HttpResponse,get_list_or_404,redirect,get_object_or_404
from django.urls import reverse
from django.template import loader
import datetime
from dashboard.models import Compagnie,Ville
from client.models import Billet,EtatBillet
from .models import Ligne,InfoLigne,Bus,Utilisateur
from django.contrib.auth.decorators import login_required
from .forms import InfoligneForm,UtilisateurForm,RechercherUtilisateur,RechercheBillet

ville= Ville.objects.all()
ligne= Ligne.objects.all()
infln= InfoLigne.objects.all()
comp= Compagnie.objects.all()
bus= Bus.objects.all()
dnow= datetime.date.today()
utilisateur=Utilisateur.objects.all()

def connexion_compagnie(request, nom_comp):
    comp_id = Compagnie.objects.filter(nom_cp=nom_comp).values_list('id', flat=True).first()
    comp=Compagnie.objects.filter(nom_cp=nom_comp)
    message = ''
    
    if request.method == 'POST':
        connexion = RechercherUtilisateur(request.POST)
        
        if connexion.is_valid():
            donnees = connexion.cleaned_data
            username = donnees['nom_utilisateur']
            password = donnees['pw_user']
            user_id = Utilisateur.objects.filter(nom_utilisateur=username, pw_user=password).values_list('id', flat=True).first()
            
            context = {'form': connexion}
            
            if user_id is not None:
                user_cp_id = Utilisateur.objects.filter(nom_utilisateur=username, pw_user=password).values_list('compagnie_id', flat=True).first()
                user_cp_grade = Utilisateur.objects.filter(nom_utilisateur=username, pw_user=password).values_list('grade_id', flat=True).first()
                
                if user_cp_id == comp_id:
                    if user_cp_grade == 2:
                        return redirect(reverse('companyman:espace_compagnie_manager', args=[user_id]))
                    elif user_cp_grade == 3:
                        return redirect(reverse('companyman:espace_compagnie_agent', args=[comp_id]))
                else:
                    message = "Vous n'êtes pas de cette compagnie."
                    return render(request, 'err_msg.html', {'message': message})
            else:
                message = 'Identifiant ou mot de passe incorrect.'
                return render(request, 'err_msg.html', {'message': message})
        else:
            context['form'] = connexion
    else:
        connexion = RechercherUtilisateur()
    
    return render(request, 'connexion_compagnie.html', {'form': connexion, 'message': message, 'comp':comp})


def espace_compagnie_manager(request, user_id):
    user = get_object_or_404(Utilisateur, pk=user_id)
    user_comp_id = Utilisateur.objects.filter(id=user_id).values_list('compagnie_id',flat=True).first()
    
    comp = Compagnie.objects.filter(id=user_comp_id).first()

    if user is None or comp is None:
        message = "Vous n'êtes pas autorisé à accéder à cet espace !"
        return render(request, 'err_msg.html', {'message': message})

    lignes = Ligne.objects.all()
    context = {'utilisateur': user, 'lignes': lignes, 'comp': comp}

    return render(request, 'espace_compagnie_manager.html', context)



def espace_compagnie_agent(request, user_id):
    user = get_object_or_404(Utilisateur, pk=user_id)
    user_comp_id = Utilisateur.objects.filter(id=user_id).values_list('compagnie_id',flat=True).first()
    
    comp = Compagnie.objects.filter(id=user_comp_id).last()

    if user is None or comp is None:
        message = "Vous n'êtes pas autorisé à accéder à cet espace !"
        return render(request, 'err_msg.html', {'message': message})

    lignes = Ligne.objects.all()
    context = {'utilisateur': user, 'lignes': lignes, 'comp': comp}

    return render(request, 'espace_compagnie_agent.html', context)


def creer_utilisateur(request,comp_id):
    compagnie=get_object_or_404(Compagnie, pk=comp_id)
    if request.method == 'POST':
        formulaire = UtilisateurForm(request.POST)
        context = {
            'comp': compagnie,
            'form': formulaire,
        }
        if formulaire.is_valid():
            donnees = formulaire.cleaned_data
            user = UtilisateurForm.objects.create(
                grade_id=donnees['grade_id'],
                nom_user=donnees['nom_user'],
                prenom_user=donnees['prenom_user'],
                email_user=donnees['email_user'],
                nom_utilisateur=donnees['nom_utilisateur'],
                pw_user=donnees['pw_user'],
                compagnie_id=comp_id,
            )
            if donnees['pw_user']==donnees['pw_user2']:
                user.save()
                return redirect(reverse('companyman:user_detail_view', args=[user.pk]))
        else:
            context['form'] = formulaire
    else:
        formulaire = UtilisateurForm()
        context = {
            'form': formulaire,
            'comp':compagnie,
        }
    return render(request, 'creer_utilisateur.html', context)


# @login_required
def ajouter_infoligne(request,comp_id):
    leslignes=[(l.id,l.libelle) for l in Ligne.objects.all()]
    # Filtrer les bus en fonction de la compagnie connectée
    compagnie_id = get_object_or_404(Compagnie,pk=comp_id)  
    lesbus = Bus.objects.filter(compagnie_id=compagnie_id)
    form=InfoligneForm(request.POST or None)
    form.fields['bus_id'].queryset = lesbus  # Définir la queryset de bus pour le champ "bus_id" du formulaire
    if form.is_valid():
        form.save()
        return redirect('companyman:liste_infolignes')
    context={
        'form':form,
    }
    return render(request,'ajouter_infoligne.html',context)

def liste_infolignes(request,comp_id):
    context={'comp':get_object_or_404(Compagnie, pk=comp_id),
             'infln':infln.filter(compagnie_id=comp_id),
             }
    return render(request,'liste_infolignes.html',context)

    


def recherche_billet(request):
    if request.method == 'POST':
        recherche = RechercheBillet(request.POST)
        if recherche.is_valid():
            donnees = recherche.cleaned_data
            code = donnees['code_billet']
            resultat = Billet.objects.filter(code_billet=code).first()
            if resultat is not None:
                id_billet = resultat.id
                return redirect(reverse('companyman:validation_billet2', args=[id_billet]))
            else:
                message = "Aucun billet ne correspond à ce code"
                return HttpResponse(message)
    else:
        recherche = RechercheBillet()
    context = {
        'recherche': recherche,
    }
    return render(request, 'valider_billet1.html', context)

def validation_billet(request, billet_id):
    billet = get_object_or_404(Billet, id=billet_id)
    infoln = get_object_or_404(InfoLigne, id=billet.infoligne_id.id)
    etatb=get_object_or_404(EtatBillet, id=billet.etat_billet.id)
    context = {
        'billet': billet,
        'infoln': infoln,
        'ligne': ligne,
        'etat':etatb,
    }
    
    return render(request, 'validation_billet2.html', context)


def valider_billet(request, billet_id):
    billet = get_object_or_404(Billet, id=billet_id)
    billet.etat_billet = EtatBillet.objects.get(id=2)
    billet.bl_valide = False
    billet.save()

    return redirect('companyman:validation_billet3', billet_id=billet.id)