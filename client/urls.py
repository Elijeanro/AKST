from django.urls import path
from . import views

app_name="client"

urlpatterns = [
    path('',views.accueil_view,name='accueil'),
    path('suggestion/',views.suggestionForm,name='suggestion'),
    path('etape1/',views.reservation1_view,name='etape1'),
    path('etape2/details/<int:billet_id>/',views.billet_detail_view,name='billet_detail_view'),
    path('etape2/<int:res_id>/',views.reservation2_view,name='etape2'),
    path('infoligne/<int:ln_id>/',views.infoligne_view, name='infoligne'),
    
]

