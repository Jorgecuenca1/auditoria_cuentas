from django.contrib import admin
from .models import Glosa, TipoGlosa, SubtipoGlosa, SubCodigoGlosa, TipoGlosaRespuestaIPS, SubtipoGlosaRespuestaIPS, HistorialGlosa

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
    list_display = ('factura', 'ips', 'paciente', 'estado', 'fecha_glosa', 'fecha_respuesta', 'aceptada')
    list_filter = ('estado', 'aceptada', 'fecha_glosa', 'fecha_respuesta', 'ips')
    search_fields = ('factura__numero', 'paciente__numero_documento', 'ips__entidad_nombre')
    readonly_fields = ('fecha_glosa',)
    fieldsets = (
        ('Información General', {
            'fields': ('factura', 'ips', 'paciente', 'estado', 'aceptada')
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

@admin.register(HistorialGlosa)
class HistorialGlosaAdmin(admin.ModelAdmin):
    list_display = ('glosa', 'accion', 'usuario', 'fecha_cambio', 'estado_anterior', 'estado_nuevo')
    list_filter = ('accion', 'fecha_cambio', 'usuario')
    search_fields = ('glosa__id', 'glosa__factura__numero', 'usuario__username', 'descripcion_cambio')
    readonly_fields = ('fecha_cambio', 'ip_address', 'user_agent')
    ordering = ('-fecha_cambio',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('glosa', 'usuario', 'accion', 'fecha_cambio')
        }),
        ('Detalles del Cambio', {
            'fields': ('estado_anterior', 'estado_nuevo', 'valor_anterior', 'valor_nuevo', 'descripcion_cambio')
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # No permitir crear registros manualmente desde el admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # No permitir editar registros del historial
        return False