from django.contrib import admin
from .models import (
    Factura, Paciente, Contrato, RipsConsulta, RipsMedicamento,
    RipsProcedimiento, RipsHospitalizacion, RipsOtroServicio, ManualTarifario,
    UsuariosNoAptos, CodigoDevolucion, SubcodigoDevolucion, Devolucion, Lote
)

@admin.register(UsuariosNoAptos)
class UsuariosNoAptosAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'fecha_registro')
    search_fields = ('cedula', 'nombre')

@admin.register(CodigoDevolucion)
class CodigoDevolucionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion')

@admin.register(SubcodigoDevolucion)
class SubcodigoDevolucionAdmin(admin.ModelAdmin):
    list_display = ('subcodigo', 'descripcion', 'codigo_padre')
    list_filter = ('codigo_padre',)

admin.site.register(Factura)
admin.site.register(Paciente)
admin.site.register(Contrato)
admin.site.register(RipsConsulta)
admin.site.register(RipsMedicamento)
admin.site.register(RipsProcedimiento)
admin.site.register(RipsHospitalizacion)
admin.site.register(RipsOtroServicio)
admin.site.register(ManualTarifario)
admin.site.register(Devolucion)
admin.site.register(Lote)