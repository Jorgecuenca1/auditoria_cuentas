from django.urls import path
from .views import radicar_factura

app_name = 'facturacion'

urlpatterns = [
    path('radicar/', radicar_factura, name='radicar_factura'),
]
