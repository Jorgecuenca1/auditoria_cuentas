from django.contrib import admin
from .models import Glosa, TipoGlosa, SubtipoGlosa, SubCodigoGlosa, TipoGlosaRespuestaIPS, SubtipoGlosaRespuestaIPS

@admin.register(TipoGlosa)
class TipoGlosaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(SubtipoGlosa)
class SubtipoGlosaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo_glosa')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo_glosa',)

@admin.register(SubCodigoGlosa)
class SubCodigoGlosaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'subtipo_glosa')
    search_fields = ('codigo', 'nombre')
    list_filter = ('subtipo_glosa',)

@admin.register(TipoGlosaRespuestaIPS)
class TipoGlosaRespuestaIPSAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(SubtipoGlosaRespuestaIPS)
class SubtipoGlosaRespuestaIPSAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo_glosa_respuesta')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo_glosa_respuesta',)

@admin.register(Glosa)
class GlosaAdmin(admin.ModelAdmin):
    list_display = ('factura', 'paciente', 'estado', 'fecha_glosa', 'fecha_respuesta', 'aceptada')
    list_filter = ('estado', 'aceptada', 'fecha_glosa', 'fecha_respuesta')
    search_fields = ('factura__numero', 'paciente__numero_documento')
    readonly_fields = ('fecha_glosa',)
    fieldsets = (
        ('Información General', {
            'fields': ('factura', 'paciente', 'estado', 'aceptada')
        }),
        ('Detalle de la Glosa', {
            'fields': ('tipo_glosa', 'subtipo_glosa', 'subcodigo_glosa', 'descripcion', 'valor_glosado')
        }),
        ('Respuesta de la IPS', {
            'fields': ('descripcion_respuesta', 'archivo_soporte_respuesta', 'tipo_glosa_respuesta', 'subtipo_glosa_respuesta')
        }),
        ('Fechas', {
            'fields': ('fecha_glosa', 'fecha_respuesta')
        }),
    )