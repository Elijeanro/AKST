from django.shortcuts import render,HttpResponse,get_object_or_404,redirect,HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from . import forms,models
import datetime
from dashboard.models import Compagnie,Ville
from companyman.models import Ligne,InfoLigne,Bus
from .functions import code
from django.db.models.query import QuerySet
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from reportlab.lib.pagesizes import letter
from xhtml2pdf import pisa
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from django.template import Context
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart




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
    ligne= Ligne.objects.all()
    infln= InfoLigne.objects.all()
    context={'rdt':lesdates,
             'infln':infln,
             'lignes':ligne,}
    return render(request,'listechoix.html',context)

def info_par_ligne_view(request, ligne):
    la_ligne = Ligne.objects.filter(libelle=ligne).first()
    if la_ligne:
        id_ligne = la_ligne.id
        context = {
            'la_ligne': la_ligne,
            'infln': InfoLigne.objects.filter(ligne_id=id_ligne,date_dep__gt=datetime.datetime.now(),place_restante__gt=0)
        }
        return render(request, 'info_par_ligne.html', context)
    else:
        # Gérer le cas où la ligne n'existe pas
        return HttpResponse("La ligne spécifiée n'existe pas.")



def infoligne_view(request,ln_id):
    context={'ln':get_object_or_404(Ligne, pk=ln_id),
             'infln':infln.filter(ligne_id=ln_id, date_dep__gte=datetime.datetime.now(),place_restante__gt=0),
             }
    return render(request,'infoligne.html',context)

def update_places_disponibles(infoligne_id, nb_places_res):
    """
    Fonction pour mettre à jour le nombre de places disponibles dans le modèle Infoligne.
    """
    infoligne = InfoLigne.objects.get(pk=infoligne_id)
    infoligne.place_restante -= nb_places_res
    infoligne.save()


# def send_email(subject, message, recipient):
#     # Paramètres de connexion au serveur SMTP
#     smtp_host = 'smtp.example.com'
#     smtp_port = 587
#     smtp_username = 'your_smtp_username'
#     smtp_password = 'your_smtp_password'

#     # Adresse e-mail de l'expéditeur et du destinataire
#     sender = 'sender@example.com'
#     receiver = recipient

#     # Création du message e-mail
#     msg = MIMEMultipart()
#     msg['From'] = sender
#     msg['To'] = receiver
#     msg['Subject'] = subject
#     msg.attach(MIMEText(message, 'plain'))

#     # Envoi de l'e-mail via SMTP
#     with smtplib.SMTP(smtp_host, smtp_port) as server:
#         server.starttls()
#         server.login(smtp_username, smtp_password)
#         server.send_message(msg)



def reservation2_view(request, res_id):
    res = get_object_or_404(InfoLigne, pk=res_id)
    if request.method == 'POST':
        formulaire = forms.BilletForm(request.POST)
        context = {
            'res': res,
            'inf': infln.get(pk=res_id),
            'form1': formulaire,
            'lecode': lecode,
            'prix': InfoLigne.objects.filter(id=res_id).values_list('prix', flat=True),
        }
        if formulaire.is_valid():
            donnees = formulaire.cleaned_data
            if donnees['place'] <= res.place_restante:
                montant = models.Billet(place=donnees['place'], prix=context['prix'])
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
                update_places_disponibles(context['inf'].pk, donnees['place'])
                # Envoi de l'e-mail de confirmation
                # subject = 'Confirmation de réservation'
                # message = 'Votre réservation a été effectuée avec succès.'
                # recipient = donnees['email_clt']
                # send_email(subject, message, recipient)

                return redirect(reverse('client:billet_detail_view', args=[billet.pk]))
            else:
                max_place = res.place_restante
                message = f"Le nombre de places que vous pouvez choisir est maximum {max_place}"
                context['message'] = message
        else:
            context['form1'] = formulaire
    else:
        formulaire = forms.BilletForm()
        context = {
            'res': get_object_or_404(InfoLigne, pk=res_id),
            'inf': infln.get(pk=res_id),
            'form1': formulaire,
        }
    return render(request, 'reservation_etape2.html', context)

def billet_detail_view(request, billet_id):
    billet = get_object_or_404(models.Billet, pk=billet_id)
    infoln = get_object_or_404(InfoLigne, pk=billet.infoligne_id.pk)
    context = {
        'billet': billet,
        'infoln' : infoln,
        'ligne' : ligne,
        }
    return render(request, 'billet_detail.html', context)


def generate_pdf(request, billet_id):
    # Get the Billet object with the specified ID
    billet = models.Billet.objects.get(id=billet_id)

    # Create a new PDF document using ReportLab SimpleDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Billet_{}-{}.pdf"'.format(
        billet.nom_clt.replace(" ", "_"), billet.id
    )
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Create a list to hold the PDF content
    elements = []

    # Define custom styles for the PDF
    styles = getSampleStyleSheet()
    heading_style = styles['Heading1']
    heading_style.alignment = 1
    paragraph_style = ParagraphStyle(
        'CustomParagraphStyle',
        parent=styles['Normal'],
        fontSize=16,
        leading=18,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.black,
    )

    # Add the header with custom text
    header_text = "AKST, VOYAGEZ PLUS FACILEMENT"
    header_style = ParagraphStyle(
        'CustomHeaderStyle',
        parent=styles['Heading2'],
        fontSize=16,
        leading=18,
        spaceAfter=12,
        spaceBefore=0,  # Remove the space before the header
        textColor=colors.blue,
        alignment=1  # Align the header text to the center
    )
    elements.append(Paragraph(header_text, header_style))

    # Add content to the PDF
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Votre Billet de voyage", heading_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Ligne: {} - {}".format(
        billet.infoligne_id.ligne_id.ville_dep.nom_ville,
        billet.infoligne_id.ligne_id.ville_arr.nom_ville), paragraph_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Nom: {}".format(billet.nom_clt), paragraph_style))
    elements.append(Paragraph("Prénom: {}".format(billet.prenom_clt), paragraph_style))
    elements.append(Paragraph("Téléphone: {}".format(billet.telephone_clt), paragraph_style))
    elements.append(Paragraph("Email: {}".format(billet.email_clt), paragraph_style))
    elements.append(Spacer(1, 20))

    # Create a table for additional details
    data = [
        ["Code Billet", billet.code_billet],
        ["Prix Unitaire", "{} francs CFA".format(billet.prix)],
        ["Nombre de places", str(billet.place)],
        ["Montant Total", "{} francs CFA".format(billet.montant_billet)],
        ["Etat du billet", billet.etat_billet.libelle],
        ["Billet valide", str(billet.bl_valide)],
        ["Date et heure de départ", billet.infoligne_id.date_dep.strftime("%d-%m-%Y / %H:%M:%S")],
        ["Date et heure d'arrivée", billet.infoligne_id.date_arr.strftime("%d-%m-%Y / %H:%M:%S")],
    ]

    # Créer le style de la cellule avec une taille de police spécifique
    cell_style = ParagraphStyle(
        'CustomCellStyle',
        parent=styles['Normal'],
        fontSize=15,
        leading=20,
        textColor=colors.black,
    )

    # Créer le tableau en spécifiant le style des cellules
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Appliquer le style des cellules au tableau
    for i in range(len(data)):
        for j in range(len(data[i])):
            cell = Paragraph(data[i][j], cell_style)
            table_style.add('VALIGN', (j, i), (j, i), 'MIDDLE')
            table_style.add('LEFTPADDING', (j, i), (j, i), 5)
            table_style.add('RIGHTPADDING', (j, i), (j, i), 5)
            table_style.add('TOPPADDING', (j, i), (j, i), 8)
            table_style.add('BOTTOMPADDING', (j, i), (j, i), 8)
            table_style.add('FONTSIZE', (j, i), (j, i), 15)

    # Créer le tableau avec le nouveau style des cellules
    table = Table(data, style=table_style, hAlign='CENTER')
    elements.append(table)

    # Build the PDF document
    pdf.build(elements)

    # Get the PDF content from the buffer and return the response
    pdf_buffer.seek(0)
    response.write(pdf_buffer.getvalue())
    pdf_buffer.close()

    return response

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
    infos = InfoLigne.objects.filter(bus_id__compagnie_id=cp_id)
    context={
        'cp':get_object_or_404(Compagnie, pk=cp_id),
        'infos': infos,
    }
    return render(request,'lacompagnie.html',context)
