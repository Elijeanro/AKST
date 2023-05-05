from django.shortcuts import render

def compagnies_view(request):
    return render(request,'listeCompagnies.html')
