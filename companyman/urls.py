from django.urls import path
from . import views

app_name='companyman'

urlpatterns = [
    path('compagnie/',views.compagnie_view,name='compagnie'),
    path('grade/',views.grade_view,name='grade'),
    path('ville/',views.ville_view,name='ville'),
]