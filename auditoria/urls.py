# 3) auditoria/urls.py
from django.urls import path, include
from . import views, api_views

app_name = 'auditoria'

urlpatterns = [
    path('radicados/', views.lista_radicados, name='lista_radicados'),
    path('factura/<int:factura_id>/', views.auditar_factura, name='auditar_factura'),
    path('factura/<int:factura_id>/glosas/', views.lista_glosas, name='lista_glosas'),
    path('glosa/<int:glosa_id>/responder/', views.responder_glosa, name='responder_glosa'),
    path('glosas-pendientes/', views.glosas_pendientes, name='glosas_pendientes'),
    path('devoluciones/', views.lista_devoluciones, name='lista_devoluciones'),
    path('factura/<int:factura_id>/devolver/', views.devolver_factura_manual, name='devolver_factura_manual'),

    # URLs para Reportes
    path('reportes/glosas/', views.reporte_glosas, name='reporte_glosas'),
    path('reportes/cartera/', views.reporte_cartera, name='reporte_cartera'),
    path('reportes/auditorias/', views.reporte_auditorias, name='reporte_auditorias'),
    path('reportes/glosas-por-paciente/', views.reporte_glosas_por_paciente, name='reporte_glosas_por_paciente'),
    path('reportes/glosas-por-tipo-item/', views.reporte_glosas_por_tipo_item, name='reporte_glosas_por_tipo_item'),
    path('reportes/auditoria-detalle/<int:factura_id>/', views.reporte_auditoria_detalle, name='reporte_auditoria_detalle'),
    path('reportes/auditoria-lote/', views.reporte_auditoria_lote, name='reporte_auditoria_lote'),

    # API endpoints
    path('api/', include('auditoria.api_urls')),
]
