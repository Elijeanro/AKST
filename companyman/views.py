from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.urls import reverse
from django.template import loader
from dashboard.models import Compagnie, Ville
from client.models import Billet, EtatBillet
from .models import Ligne, InfoLigne, Bus, Utilisateur, Etat
from django.contrib.auth.decorators import login_required
from .forms import InfoligneForm, UtilisateurForm, RechercherUtilisateur,RechercherUtilisateur2, RechercheBillet,BusForm,RechercherBus
from datetime import timedelta, datetime, date
from django.contrib import messages
from django.db.models import F,Sum
from django.utils import timezone
from . tasks import update_billets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail import send_mail

ville= Ville.objects.all()
ligne= Ligne.objects.all()
infln= InfoLigne.objects.all()
comp= Compagnie.objects.all()
bus= Bus.objects.all()
dnow= date.today()
utilisateur=Utilisateur.objects.all()



def connexion_compagnie(request, nom_comp):
    comp_id = Compagnie.objects.filter(nom_cp=nom_comp).values_list('id', flat=True).first()
    comp = Compagnie.objects.filter(nom_cp=nom_comp).first()
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
                        return redirect(reverse('companyman:espace_compagnie_agent', args=[user_id]))
                else:
                    message = "Vous n'êtes pas de cette compagnie."
                    return redirect(reverse('companyman:err_msg', args=[nom_comp]) + f'?message={message}')
            else:
                message = 'Identifiant ou mot de passe incorrect.'
                return redirect(reverse('companyman:err_msg', args=[nom_comp]) + f'?message={message}')
        else:
            context['form'] = connexion
    else:
        connexion = RechercherUtilisateur()
    
    return render(request, 'connexion_compagnie.html', {'form': connexion, 'message': message, 'comp': comp})

def err_msg(request, comp):
    comp = get_object_or_404(Compagnie, nom_cp=comp)
    message = request.GET.get('message', '')
    
    return render(request, 'err_msg.html', {'comp': comp, 'message': message})

def espace_compagnie_manager(request, user_id):
    billets = Billet.objects.filter(infoligne_id__date_dep__lt=timezone.now(), etat_billet=1)
    
    # Mettre à jour les billets
    for billet in billets:
        billet.etat_billet_id = 4
        billet.save()
    user = get_object_or_404(Utilisateur, pk=user_id)
    user_comp_id = user.compagnie_id.id
    bus_ids = Bus.objects.filter(compagnie_id=user_comp_id).values_list('id', flat=True)
    bus = Bus.objects.filter(id__in=bus_ids)
    maintenant = datetime.now()

    # Remplacer les secondes et les fractions de seconde par 0
    nouveau_datetime = maintenant.replace(second=0, microsecond=0)

    # Formater la date et l'heure selon le format souhaité
    dnow = nouveau_datetime.strftime("%Y-%m-%d %H:%M")
    lignes = Ligne.objects.all()
    villes = Ville.objects.all()

    infln_ids = InfoLigne.objects.filter(bus_id__in=bus_ids).values_list('id', flat=True)
    billets = Billet.objects.filter(infoligne_id__in=infln_ids)
    enattente = Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=1)
    consommes = Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=2)
    annules = Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=3)
    expires = Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=4)
    nb_reserv=billets.count()
    nb_valid= Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=2).count()
    nb_expir= Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=4).count()
    nb_annul= Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=3).count()
    nb_en_attente= Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=1).count()
    infln = InfoLigne.objects.filter(bus_id__in=bus_ids)
    passe = InfoLigne.objects.filter(bus_id__in=bus_ids, date_dep__lt=dnow)
    encours = InfoLigne.objects.filter(bus_id__in=bus_ids, date_dep=dnow)
    a_venir = InfoLigne.objects.filter(bus_id__in=bus_ids, date_dep__gt=dnow)
    
    # le chiffre d'affaire
    CA = Billet.objects.filter(infoligne_id__in=infln_ids,etat_billet=2).aggregate(Sum('montant_billet'))['montant_billet__sum']
    
    comp = Compagnie.objects.filter(id=user_comp_id).first()

    if user is None or comp is None:
        message = "Vous n'êtes pas autorisé à accéder à cet espace !"
        return render(request, 'err_msg.html', {'message': message})

    context = {'utilisateur': user,
               'lignes': lignes,
               'comp': comp,
               'billets': billets,
               'bus': bus,
               'villes': villes,
               'infln':infln,
               'nb_reserv':nb_reserv,
               'nb_valid':nb_valid,
               'nb_annul':nb_annul,
               'nb_en_attente':nb_en_attente,
               'nb_expir':nb_expir,
               'CA':CA,
               'enattente':enattente,
               'consommes':consommes,
               'expires':expires,
               'annules':annules,
               'dnow':dnow,
               'passe':passe,
               'encours':encours,
               'a_venir':a_venir,
               }

    return render(request, 'espace_compagnie_manager.html', context)



def espace_compagnie_agent(request, user_id):
    user = get_object_or_404(Utilisateur, pk=user_id)
    user_comp_id = user.compagnie_id.id
    bus_ids = Bus.objects.filter(compagnie_id=user_comp_id).values_list('id', flat=True)
    bus = Bus.objects.filter(id__in=bus_ids)
    maintenant = datetime.now()

    # Remplacer les secondes et les fractions de seconde par 0
    nouveau_datetime = maintenant.replace(second=0, microsecond=0)

    # Formater la date et l'heure selon le format souhaité
    dnow = nouveau_datetime.strftime("%Y-%m-%d %H:%M")
    lignes = Ligne.objects.all()
    villes = Ville.objects.all()

    infln_ids = InfoLigne.objects.filter(bus_id__in=bus_ids).values_list('id', flat=True)
    billets = Billet.objects.filter(infoligne_id__in=infln_ids)
    infln = InfoLigne.objects.filter(bus_id__in=bus_ids)
    passe = InfoLigne.objects.filter(bus_id__in=bus_ids, date_dep__lt=dnow)
    encours = InfoLigne.objects.filter(bus_id__in=bus_ids, date_dep=dnow)
    a_venir = InfoLigne.objects.filter(bus_id__in=bus_ids, date_dep__gt=dnow)
    comp = Compagnie.objects.filter(id=user_comp_id).first()
    if user is None or comp is None:
        message = "Vous n'êtes pas autorisé à accéder à cet espace !"
        return render(request, 'err_msg.html', {'message': message})

    lignes = Ligne.objects.all()
    context = {'utilisateur': user,
               'lignes': lignes,
               'comp': comp,
               'billets': billets,
               'bus': bus,
               'villes': villes,
               'infln':infln,
               'dnow':dnow,
               'passe':passe,
               'encours':encours,
               'a_venir':a_venir,
               }

    return render(request, 'espace_compagnie_agent.html', context)

def recherche_billet(request,comp_id,user_id):
    comp = get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    if request.method == 'POST':
        recherche = RechercheBillet(request.POST)
        if recherche.is_valid():
            donnees = recherche.cleaned_data
            code = donnees['code_billet']
            resultat = Billet.objects.filter(code_billet=code).first()
            if resultat is not None:
                id_billet = resultat.id
                return redirect(reverse('companyman:validation_billet2', args=[id_billet,user_id]))
            else:
                message = "Aucun billet ne correspond à ce code"
                return HttpResponse(message)
    else:
        recherche = RechercheBillet()
    context = {'recherche': recherche , 'comp' : comp, 'user':user}
    return render(request, 'valider_billet1.html', context)


def validation_billet(request, billet_id, user_id):
    billet = get_object_or_404(Billet, id=billet_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    infoln = get_object_or_404(InfoLigne, id=billet.infoligne_id.id)
    ligne = get_object_or_404(Ligne, id=infoln.ligne_id.id)
    etatb = get_object_or_404(EtatBillet, id=billet.etat_billet.id)
    comp = get_object_or_404(Compagnie,id=infoln.bus_id.compagnie_id.id) 
    datebillet = infoln.date_dep.date()
    dnow = datetime.today().date()
    print("etat:", etatb.id)
    print("datebillet:", datebillet)
    print("today:", datetime.today().date())
    context = {
        'billet': billet, 
        'infoln': infoln, 
        'ligne': ligne, 
        'etat': etatb, 
        'comp':comp, 
        'dnow':dnow, 
        'datebillet':datebillet,
        'user':user
        }
    return render(request, 'valider_billet2.html', context)
from django.conf import settings

def valider_billet(request, billet_id, user_id):
    billet = get_object_or_404(Billet, id=billet_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    billet.etat_billet = EtatBillet.objects.get(id=2)
    billet.bl_valide = False
    billet.save()
    # Envoyer l'e-mail de confirmation
    subject = 'Confirmation de réservation'
    message = f"Votre billet a été validé avec succès.\nVeuillez embarquer sans plus attendre\n\nNom: {billet.nom_clt}\nPrénom: {billet.prenom_clt}\nLigne: {billet.infoligne_id.ligne_id.libelle}\nCompagnie: {billet.infoligne_id.bus_id.compagnie_id.nom_cp}\nTarif: {billet.prix}\nNombre de place: {billet.place}\nMontant total: {billet.montant_billet}\nCode du billet: {billet.code_billet}\nID de paiement: {billet.id_paiement}"
    email_from = settings.EMAIL_HOST_USER
    recipient = billet.email_clt
    send_mail(subject, message, email_from, [recipient])
    
    billet = get_object_or_404(Billet, id=billet_id)
    infoln = get_object_or_404(InfoLigne, id=billet.infoligne_id.id)
    ligne = get_object_or_404(Ligne, id=infoln.ligne_id.id)
    etatb = get_object_or_404(EtatBillet, id=billet.etat_billet.id)
    comp = get_object_or_404(Compagnie,id=infoln.bus_id.compagnie_id.id) 
    context = {'billet': billet, 'infoln': infoln, 'ligne': ligne, 'etat': etatb, 'comp':comp, 'user':user}
    return render(request, 'valider_billet3.html', context)

def creer_utilisateur(request, comp_id, user_id):
    compagnie = get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    if request.method == 'POST':
        formulaire = UtilisateurForm(request.POST)

        if formulaire.is_valid():
            donnees = formulaire.cleaned_data
            grade_id=donnees['grade_id']
            nom_user=donnees['nom_user']
            prenom_user=donnees['prenom_user']
            email_user=donnees['email_user']
            if Utilisateur.objects.filter(grade_id=grade_id,nom_user=nom_user,prenom_user=prenom_user,email_user=email_user).exists():
                messages.error(request, "Cet utilisateur existe déjà ! ")
                
            elif donnees['pw_user'] == request.POST.get('pw_user2'):
                user = Utilisateur.objects.create(
                    grade_id=grade_id,
                    nom_user=nom_user,
                    prenom_user=prenom_user,
                    email_user=email_user,
                    nom_utilisateur=donnees['nom_utilisateur'],
                    pw_user=donnees['pw_user'],
                    compagnie_id=compagnie,
                    personnel_actif=donnees['personnel_actif'],
                )

                return redirect(reverse('companyman:user_detail_view', args=[user.pk]))
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            messages.error(request, "Le formulaire n'est pas valide.")
    else:
        formulaire = UtilisateurForm()

    context = {
        'form': formulaire,
        'comp': compagnie,
        'user':user,
    }
    return render(request, 'creer_utilisateur.html', context)


def user_detail_view(request, user_id):
    user = get_object_or_404(Utilisateur, pk=user_id)
    comp_id = user.compagnie_id.id
    comp = get_object_or_404(Compagnie, id=comp_id)
    utilisateur = Utilisateur.objects.all()
    context = {
        'user': user,
        'comp': comp,
        'utilisateur': utilisateur,
    }
    messages.success(request, "Utilisateur créé avec succès.")
    return render(request, 'user_detail_view.html', context)


def delete_user1(request, comp_id, user_id):
    comp = get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    users = Utilisateur.objects.filter(compagnie_id=comp_id)
    context = {
        'comp': comp,
        'users': users,
        'user' : user,
    }
    return render(request, 'supprimer_utilisateur.html', context)


def delete_user2(request, user_id):
    user = get_object_or_404(Utilisateur, pk=user_id)
    comp_id = user.compagnie_id.id

    user.personnel_actif = False
    user.save(update_fields=['personnel_actif'])

    messages.success(request, "L'utilisateur a été supprimé avec succès.")
    return redirect('companyman:supprimer_utilisateur', comp_id=comp_id)


def liste_agents(request, comp_id, user_id):
    comp = get_object_or_404(Compagnie, pk=comp_id)
    users = Utilisateur.objects.filter(compagnie_id=comp_id)
    utilisateur = Utilisateur.objects.all()
    return render(request, 'liste_agents.html', {'comp': comp, 'users': users, 'utilisateur': utilisateur})


def liste_lignes(request, comp_id, user_id):
    comp = get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    users = Utilisateur.objects.filter(compagnie_id=comp_id)
    lignes = Ligne.objects.all()
    return render(request, 'liste_lignes.html', {'lignes': lignes, 'users': users, 'user':user, 'comp': comp})


def liste_bus(request, user_id):
    bus = Bus.objects.all()
    user = get_object_or_404(Utilisateur, pk=user_id)
    utilisateur = Utilisateur.objects.all()
    return render(request, 'liste_bus.html', {'bus': bus, 'utilisateur': utilisateur, 'user' : user})


def ajouter_infoligne(request, comp_id, user_id):
    comp = get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    infln = None

    if request.method == 'POST':
        form = InfoligneForm(request.POST, compagnie_id=comp_id)

        if form.is_valid():
            donnees = form.cleaned_data
            ligne = Ligne.objects.filter(id=donnees['ligne_id'].id).first()
            duree_trajet = ligne.duree_trajet

            date_dep = donnees['date_dep']
            date_arr = date_dep + duree_trajet

            infln = InfoLigne.objects.create(
                date_dep=date_dep,
                date_arr=date_arr,
                prix=donnees['prix'],
                bus_id=donnees['bus_id'],
                ligne_id=donnees['ligne_id'],
                place_restante=donnees['place_restante'],
            )
            infln.save()

            return redirect(reverse('companyman:detail_infoligne', args=[infln.pk]))

        else:
            messages.error(request, "Une erreur s'est produite.")
    else:
        form = InfoligneForm(compagnie_id=comp_id)

        
    context = {'comp': comp, 'form': form, 'user':user,}
    return render(request, 'ajouter_infoligne.html', context)


def supprimer_infoligne(request, infln_id, user_id):
    infln = get_object_or_404(InfoLigne, pk=infln_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    comp = Compagnie.objects.get(id=infln.bus_id.compagnie_id.id)
    if infln.etat_infoligne.id == 2:
        infln.etat_infoligne_id = 1
        infln.save()
        messages.success(request, "Voyage supprimé avec succès !")
        return redirect('companyman:supprimer_infoligne', infln_id=infln.id)
    else:
        messages.error(request, "Ce voyage a déjà été supprimé.")

    context = {
        'infln': infln,
        'comp_id': infln.bus_id.compagnie_id.id,
        'comp':comp,
        'user':user,
    }
    return render(request, 'supprimer_infoligne.html', context)

def infoligne_edit_view(request, infln_id, user_id):
    infln = get_object_or_404(InfoLigne, pk=infln_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    comp = Compagnie.objects.filter(id=infln.bus_id.compagnie_id.id).first()
    if request.method == 'POST':
        formulaire = InfoligneForm(request.POST, instance=infln)

        if formulaire.is_valid():
            donnees = formulaire.cleaned_data

            if infln.etat_infoligne.id == 2:
                infln.bus_id = donnees['bus_id']
                infln.prix = donnees['prix']
                infln.save()
                messages.success(request, "Succès de modification !")
                return redirect(reverse('companyman:detail_infoligne', args=[infln.pk]))

        else:
            messages.error(request, "Le formulaire n'est pas valide.")
    else:
        compagnie_id = infln.bus_id.compagnie_id.id
        
        formulaire = InfoligneForm(instance=infln, compagnie_id=compagnie_id)

    context = {
        'form': formulaire,
        'infln': infln,
        'comp':comp,
        'user':user,
    }
    return render(request, 'infoligne_edit.html', context)



def detail_infoligne(request, infln_id, user_id):
    infln = get_object_or_404(InfoLigne, pk=infln_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    comp = get_object_or_404(Compagnie, pk=infln.bus_id.compagnie_id.id)
    return render(request, 'infoligne_view.html', {'comp': comp, 'infln': infln, 'user':user})


def liste_infolignes(request, comp_id, user_id):
    comp = get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    infln = InfoLigne.objects.filter(bus_id__compagnie_id=comp_id)
    dnow = datetime.now()
    print('dnow = ',dnow)
    context = {'comp': comp, 'infln': infln, 'user':user, 'dnow':dnow}
    return render(request, 'liste_infolignes.html', context)


def ajouter_bus(request, comp_id, user_id):
    comp = get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    if request.method == 'POST':
        form = BusForm(request.POST)
        
        if form.is_valid():
            donnees = form.cleaned_data
            matricule_bus = donnees['matricule_bus']

            # Vérifier si le bus existe déjà
            if Bus.objects.filter(matricule_bus=matricule_bus).exists():
                messages.error(request, "Ce matricule de bus existe déjà.")
            else:
                bus = Bus.objects.create(
                    matricule_bus=matricule_bus,
                    nb_place=donnees['nb_place'],
                    compagnie_id=comp,
                )
                messages.success(request, "Bus ajouté avec succès.")
                return redirect(reverse('companyman:detail_bus', args=[bus.pk]))

        else:
            messages.error(request, "Une erreur s'est produite.")
    else:
        form = BusForm()

    context = {'comp': comp, 'form': form, 'user':user}
            
    return render(request, 'ajouter_bus.html', context)

def supprimer_bus(request, bus_id, user_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    comp=Compagnie.objects.filter(id=bus.compagnie_id.id).first()
    if bus.etat_bus.id==2:
        bus.etat_bus = Etat.objects.get(id=1)
        bus.save()
        messages.success(request, "Bus supprimé avec succès !")
        return redirect(reverse('companyman:listebus', args=[comp.pk]))
    else:
        messages.error(request, "Ce bus a déja été supprimé.")

    context = {
        'bus': bus,
        'comp':comp,
    }
    return render(request, 'supprimer_bus.html', context)

def detail_bus(request, bus_id, user_id):
    bus = get_object_or_404(Bus, pk=bus_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    comp = get_object_or_404(Compagnie, pk=bus.compagnie_id.id)
    
    return render(request, 'bus_detail_view.html', {'comp': comp, 'bus': bus, 'user' : user})

def forgot_password_search(request,comp_id):
    comp=get_object_or_404(Compagnie, pk=comp_id)
    if request.method == 'POST':
        recherche = RechercherUtilisateur2(request.POST)
        if recherche.is_valid():
            donnees = recherche.cleaned_data
            nom_user = donnees['nom_user']
            prenom_user = donnees['prenom_user']
            email_user = donnees['email_user']
            nom_utilisateur = donnees['nom_utilisateur']
            resultat = Utilisateur.objects.filter(nom_user=nom_user,prenom_user=prenom_user,email_user=email_user,nom_utilisateur=nom_utilisateur).first()
            if resultat is not None and resultat.compagnie_id.id==comp.id and resultat.personnel_actif:
                
                return redirect(reverse('companyman:user_detail_view', args=[resultat.pk]))
            else:
                message = "Aucune correspondance retrouvée"
                return HttpResponse(message)
    else:
        recherche = RechercherUtilisateur2()
    context = {'recherche': recherche, 'comp':comp}
    return render(request, 'forgot_password.html', context)

def edit_user_search(request,comp_id, user_id):
    comp=get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    if request.method == 'POST':
        recherche = RechercherUtilisateur2(request.POST)
        if recherche.is_valid():
            donnees = recherche.cleaned_data
            nom_user = donnees['nom_user']
            prenom_user = donnees['prenom_user']
            email_user = donnees['email_user']
            nom_utilisateur = donnees['nom_utilisateur']
            pw_user=donnees['pw_user']
            resultat = Utilisateur.objects.filter(nom_user=nom_user,prenom_user=prenom_user,email_user=email_user,nom_utilisateur=nom_utilisateur,pw_user=pw_user).first()
            if resultat is not None and resultat.compagnie_id.id==comp.id and resultat.personnel_actif:
                
                return redirect(reverse('companyman:user_edit_view', args=[resultat.pk]))
            else:
                message = "Aucune correspondance retrouvée"
                return HttpResponse(message)
    else:
        recherche = RechercherUtilisateur2()
    context = {'recherche': recherche, 'comp':comp, 'user' : user }
    return render(request, 'edit_user.html', context)


def user_edit_view(request, user_id):
    user = get_object_or_404(Utilisateur, pk=user_id)

    if request.method == 'POST':
        formulaire = UtilisateurForm(request.POST, instance=user)

        if formulaire.is_valid():
            donnees = formulaire.cleaned_data

            if donnees['pw_user'] == request.POST.get('pw_user2'):
                user.nom_utilisateur = donnees['nom_utilisateur']
                user.pw_user = donnees['pw_user']
                user.personnel_actif = donnees['personnel_actif']
                user.save()

                return redirect(reverse('companyman:user_detail_view', args=[user.pk]))
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            messages.error(request, "Le formulaire n'est pas valide.")
    else:
        formulaire = UtilisateurForm(instance=user)

    context = {
        'form': formulaire,
    }
    return render(request, 'user_edit.html', context)



def listebus_view(request, comp_id, user_id):
    comp = get_object_or_404(Compagnie, pk=comp_id)
    user = get_object_or_404(Utilisateur, pk=user_id)
    bus_ids = Bus.objects.filter(compagnie_id=comp_id).values_list('id', flat=True)
    bus = Bus.objects.filter(id__in=bus_ids)
    
    lignes = Ligne.objects.all()
    villes = Ville.objects.all()

    infln_ids = InfoLigne.objects.filter(bus_id__in=bus_ids).values_list('id', flat=True)
    billets = Billet.objects.filter(infoligne_id__in=infln_ids)
    nb_reserv=billets.count()
    nb_valid= Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=2).count()
    nb_expir= Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=4).count()
    nb_annul= Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=3).count()
    nb_en_attente= Billet.objects.filter(infoligne_id__in=infln_ids, etat_billet=1).count()
    # le chiffre d'affaire
    CA = Billet.objects.filter(etat_billet=2).aggregate(Sum('montant_billet'))['montant_billet__sum']
    infln = InfoLigne.objects.filter(bus_id__in=bus_ids)
    context = {
               'lignes': lignes,
               'comp': comp,
               'billets': billets,
               'bus': bus,
               'villes': villes,
               'user' : user,
               'infln':infln,
               'nb_reserv':nb_reserv,
               'nb_valid':nb_valid,
               'nb_annul':nb_annul,
               'nb_en_attente':nb_en_attente,
               'nb_expir':nb_expir,
               'CA':CA,
               }

    return render(request, 'listebus.html', context)