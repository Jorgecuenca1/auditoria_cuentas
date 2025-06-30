# 3) auditoria/urls.py
from django.urls import path
from .views import (
    auditar_factura, lista_radicados, lista_glosas, responder_glosa, 
    glosas_pendientes, reporte_glosas, reporte_cartera, reporte_auditorias
)

app_name = 'auditoria'

urlpatterns = [
    path('radicados/', lista_radicados, name='lista_radicados'),
    path('factura/<int:factura_id>/', auditar_factura, name='auditar_factura'),
    path('glosas/<int:factura_id>/', lista_glosas, name='lista_glosas'),
    path('glosa/<int:glosa_id>/responder/', responder_glosa, name='responder_glosa'),
    path('glosas/pendientes/', glosas_pendientes, name='glosas_pendientes'),
    # URLs de reportes
    path('reportes/glosas/', reporte_glosas, name='reporte_glosas'),
    path('reportes/cartera/', reporte_cartera, name='reporte_cartera'),
    path('reportes/auditorias/', reporte_auditorias, name='reporte_auditorias'),
]
