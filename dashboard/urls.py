from django.urls import path
from . import views

urlpatterns = [
    path('lescompagnies/',views.compagnies_view,name='lescompagnies'),
]