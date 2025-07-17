from django.contrib import admin
from .models import CuentaCartera
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Recursos para import-export
class CuentaCarteraResource(resources.ModelResource):
    class Meta:
        model = CuentaCartera
        import_id_fields = ('id',)
        export_order = ('factura', 'valor_inicial', 'valor_glosado_provisional', 'valor_glosado_definitivo', 'valor_pagable', 'estado_pago', 'fecha_creacion', 'fecha_actualizacion')


# Admin classes con import-export
@admin.register(CuentaCartera)
class CuentaCarteraAdmin(ImportExportModelAdmin):
    resource_class = CuentaCarteraResource
    list_display = ('factura', 'valor_inicial', 'valor_glosado_definitivo', 'valor_pagable', 'estado_pago', 'fecha_creacion')
    list_filter = ('estado_pago', 'fecha_creacion', 'fecha_actualizacion', 'factura__ips', 'factura__eps')
    search_fields = ('factura__numero', 'factura__ips__entidad_nombre', 'factura__eps__entidad_nombre')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        ('Información de Factura', {
            'fields': ('factura',)
        }),
        ('Valores Financieros', {
            'fields': ('valor_inicial', 'valor_glosado_provisional', 'valor_glosado_definitivo', 'valor_pagable')
        }),
        ('Estado y Fechas', {
            'fields': ('estado_pago', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )