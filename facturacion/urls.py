from django.urls import path
from .views import radicar_factura, contrato_list, contrato_create, contrato_update, tarifa_contrato_list, tarifa_contrato_create, tarifa_contrato_update, tarifa_contrato_delete

app_name = 'facturacion'

urlpatterns = [
    path('radicar/', radicar_factura, name='radicar_factura'),
    path('contratos/', contrato_list, name='contrato_list'),
    path('contratos/crear/', contrato_create, name='contrato_create'),
    path('contratos/<int:pk>/editar/', contrato_update, name='contrato_update'),
    path('contratos/update/<int:pk>/', contrato_update, name='contrato_update'),
    path('contratos/<int:contrato_pk>/tarifas/', tarifa_contrato_list, name='tarifa_contrato_list'),
    path('contratos/<int:contrato_pk>/tarifas/create/', tarifa_contrato_create, name='tarifa_contrato_create'),
    path('tarifas/update/<int:pk>/', tarifa_contrato_update, name='tarifa_contrato_update'),
    path('tarifas/delete/<int:pk>/', tarifa_contrato_delete, name='tarifa_contrato_delete'),
]
