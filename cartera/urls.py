# 5) cartera/urls.py
from django.urls import path
from .views import resumen_cartera

app_name = 'cartera'

urlpatterns = [
    path('resumen/', resumen_cartera, name='resumen_cartera'),
]