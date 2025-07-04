from django.urls import path
from .views import (
    radicar_factura, contrato_list, contrato_create, contrato_update, contrato_detail,
    tarifa_contrato_list, tarifa_contrato_create, tarifa_contrato_update, 
    tarifa_contrato_delete, lote_list, lote_create, lote_detail,
    resolucion_list, resolucion_create, resolucion_detail, resolucion_edit,
    resolucion_render_html
)

app_name = 'facturacion'

urlpatterns = [
    path('radicar/', radicar_factura, name='radicar_factura'),
    
    # URLs de Contratos
    path('contratos/', contrato_list, name='contrato_list'),
    path('contratos/crear/', contrato_create, name='contrato_create'),
    path('contratos/<int:pk>/editar/', contrato_update, name='contrato_update'),
    path('contratos/<int:pk>/', contrato_detail, name='contrato_detail'),
    
    # URLs de Tarifas de Contrato
    path('contratos/<int:contrato_pk>/tarifas/', tarifa_contrato_list, name='tarifa_contrato_list'),
    path('contratos/<int:contrato_pk>/tarifas/crear/', tarifa_contrato_create, name='tarifa_contrato_create'),
    path('tarifas/<int:pk>/editar/', tarifa_contrato_update, name='tarifa_contrato_update'),
    path('tarifas/<int:pk>/eliminar/', tarifa_contrato_delete, name='tarifa_contrato_delete'),

    # URLs para Lotes de Facturas
    path('lotes/', lote_list, name='lote_list'),
    path('lotes/crear/', lote_create, name='lote_create'),
    path('lotes/<int:pk>/', lote_detail, name='lote_detail'),

    # URLs para Resoluciones
    path('resoluciones/', resolucion_list, name='resolucion_list'),
    path('resoluciones/crear/', resolucion_create, name='resolucion_create'),
    path('resoluciones/<int:pk>/', resolucion_detail, name='resolucion_detail'),
    path('resoluciones/<int:pk>/editar/', resolucion_edit, name='resolucion_edit'),
    path('resoluciones/<int:pk>/ver-html/', resolucion_render_html, name='resolucion_render_html'),
]
