from django.shortcuts import render,HttpResponse,get_list_or_404
from django.template import loader
# from . import forms
import datetime
from dashboard.models import Compagnie,Ville
from companyman.models import Ligne,InfoLigne,Bus


ville= Ville.objects.all()
ligne= Ligne.objects.all()
infln= InfoLigne.objects.all()
comp= Compagnie.objects.all()
bus= Bus.objects.all()
dnow= datetime.date.today()


def compagnie_view(request):
    # context = {
    #     "ville":ville,
    #     "ligne": ligne,
    #     "infln": infln,
    #     "comp": comp,
    #     "lesbus": bus,
    #     "dnow": dnow,
    # }
    # template = loader.get_template("index.html")
    # return HttpResponse(template.render(context, request))
    return HttpResponse('Ma compagnie')

def ville_view(request):
    # context = {
    #     "ville":ville,
    #     "ligne": ligne,
    #     "infln": infln,
    #     "comp": comp,
    #     "lesbus": bus,
    #     "dnow": dnow,
    # }
    # template = loader.get_template("index.html")
    # return HttpResponse(template.render(context, request))
    return HttpResponse('La liste des Villes')

def grade_view(request):
    # context = {
    #     "ville":ville,
    #     "ligne": ligne,
    #     "infln": infln,
    #     "comp": comp,
    #     "lesbus": bus,
    #     "dnow": dnow,
    # }
    # template = loader.get_template("index.html")
    # return HttpResponse(template.render(context, request))
    return HttpResponse('La liste des grades')


