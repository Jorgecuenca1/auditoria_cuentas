from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import CuentaCartera

# Resource para import/export
class CuentaCarteraResource(resources.ModelResource):
    class Meta:
        model = CuentaCartera
        import_id_fields = ('id',)
        fields = ('id', 'factura', 'ips', 'eps', 'valor_inicial', 'valor_glosado', 'valor_final', 'estado_pago')

@admin.register(CuentaCartera)
class CuentaCarteraAdmin(ImportExportModelAdmin):
    resource_class = CuentaCarteraResource
    list_display = ('factura', 'ips', 'eps', 'valor_inicial', 'valor_glosado', 'valor_final', 'estado_pago')
    list_filter = ('estado_pago',)
    search_fields = ('factura__numero', 'ips__entidad_nombre', 'eps__entidad_nombre')