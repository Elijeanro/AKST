from django.urls import path
from . import views

app_name='companyman'

urlpatterns = [
    path('compagnie/<str:nom_comp>',views.connexion_compagnie,name='connexion_compagnie'),
    path('compagnie/ajouter_infoligne/<int:comp_id>',views.ajouter_infoligne,name='ajouter_infoligne'),
    path('compagnie/creer_utilisateur/<int:comp_id>',views.creer_utilisateur,name='creer_utilisateur'),
    path('validation1/',views.recherche_billet,name='validation_billet1'),
    path('validation2/<int:billet_id>/',views.validation_billet,name='validation_billet2'),
    path('validation3/<int:billet_id>/',views.valider_billet,name='validation_billet3'),
    path('compagnie/liste_infolignes/',views.liste_infolignes,name='liste_infolignes'),
    path('compagnie/ajouter_infoligne/',views.ajouter_infoligne,name='ajouter_infoligne'),
    path('espace_compagnie_manager/<int:user_id>/', views.espace_compagnie_manager, name='espace_compagnie_manager'),
    path('espace_compagnie_agent/<int:user_id>/', views.espace_compagnie_agent, name='espace_compagnie_agent'),

]