from django.urls import path
from . import views

app_name='companyman'

urlpatterns = [
    #connexion
    path('compagnie/<str:nom_comp>',views.connexion_compagnie,name='connexion_compagnie'),
    #utilisateur
    path('compagnie/creer_utilisateur/<int:comp_id>',views.creer_utilisateur,name='creer_utilisateur'),
    path('compagnie/user_detail/<int:user_id>',views.user_detail_view, name='user_detail_view'),
    path('espace_compagnie_manager/<int:user_id>/', views.espace_compagnie_manager, name='espace_compagnie_manager'),
    path('espace_compagnie_agent/<int:user_id>/', views.espace_compagnie_agent, name='espace_compagnie_agent'),
    path('compagnie/supprimer_utilisateur/<int:comp_id>', views.delete_user1, name='supprimer_utilisateur'),
    path('compagnie/supprimer_utilisateur2/<int:user_id>', views.delete_user2, name='supprimer_utilisateur2'),
    path('compagnie/mot_de_passe_oublie/<int:comp_id>',views.forgot_password_search, name= 'forgot_password'),
    path('compagnie/editer_utilisateur_recherche/<int:comp_id>',views.edit_user_search, name='edit_user_search'),
    path('compagnie/editer_utilisateur/<int:user_id>',views.user_edit_view,name='user_edit_view'),
   
    #bus
    path('compagnie/ajouter_bus/<int:comp_id>',views.ajouter_bus,name='ajouter_bus'),
    path('compagnie/detail_bus/<int:bus_id>', views.detail_bus, name='detail_bus'),
    path('compagnie/supprimer_bus/<int:bus_id>',views.supprimer_bus,name='supprimer_bus'),
    
    #voyage
    path('compagnie/ajouter_infoligne/<int:comp_id>',views.ajouter_infoligne,name='ajouter_infoligne'),
    path('compagnie/liste_infolignes/<int:comp_id>',views.liste_infolignes,name='liste_infolignes'),
    path('compagnie/detail_infoligne/<int:infln_id>', views.detail_infoligne, name='detail_infoligne'),
    path('compagnie/editer_infoligne/<int:infln_id>',views.infoligne_edit_view,name='infoligne_edit_view'),
    path('compagnie/supprimer_infoligne/<int:infln_id>',views.supprimer_infoligne,name='supprimer_infoligne'),
    
    #Billet
    path('validation1/',views.recherche_billet,name='validation_billet1'),
    path('validation2/<int:billet_id>/',views.validation_billet,name='validation_billet2'),
    path('validation3/<int:billet_id>/',views.valider_billet,name='validation_billet3'),
    #listes
    path('compagnie/<int:comp_id>/liste_agents', views.liste_agents, name='liste_agents'),
    path('compagnie/liste_lignes/<int:comp_id>', views.liste_lignes, name='liste_lignes'),
    path('compagnie/liste_des_bus/<int:comp_id>',views.listebus_view,name='listebus'),
    
    path('compagnie/<str:comp>/erreur', views.err_msg, name='err_msg'),
    
    
]