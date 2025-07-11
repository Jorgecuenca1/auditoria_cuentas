from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Glosa, TipoGlosa, SubtipoGlosa, SubCodigoGlosa, TipoGlosaRespuestaIPS, SubtipoGlosaRespuestaIPS, HistorialGlosa

# Resources para import/export
class TipoGlosaResource(resources.ModelResource):
    class Meta:
        model = TipoGlosa
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'nombre')

class SubtipoGlosaResource(resources.ModelResource):
    class Meta:
        model = SubtipoGlosa
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'nombre', 'tipo_glosa')

class SubCodigoGlosaResource(resources.ModelResource):
    class Meta:
        model = SubCodigoGlosa
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'nombre', 'subtipo_glosa')

class TipoGlosaRespuestaIPSResource(resources.ModelResource):
    class Meta:
        model = TipoGlosaRespuestaIPS
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'nombre')

class SubtipoGlosaRespuestaIPSResource(resources.ModelResource):
    class Meta:
        model = SubtipoGlosaRespuestaIPS
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'nombre', 'tipo_glosa_respuesta')

class GlosaResource(resources.ModelResource):
    class Meta:
        model = Glosa
        import_id_fields = ('id',)
        fields = ('id', 'factura', 'ips', 'paciente', 'estado', 'fecha_glosa', 'fecha_respuesta', 'aceptada', 'tipo_glosa', 'subtipo_glosa', 'subcodigo_glosa', 'descripcion', 'valor_glosado', 'descripcion_respuesta', 'tipo_glosa_respuesta', 'subtipo_glosa_respuesta')

class HistorialGlosaResource(resources.ModelResource):
    class Meta:
        model = HistorialGlosa
        import_id_fields = ('id',)
        fields = ('id', 'glosa', 'usuario', 'accion', 'fecha_cambio', 'estado_anterior', 'estado_nuevo', 'valor_anterior', 'valor_nuevo', 'descripcion_cambio', 'ip_address', 'user_agent')

@admin.register(TipoGlosa)
class TipoGlosaAdmin(ImportExportModelAdmin):
    resource_class = TipoGlosaResource
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(SubtipoGlosa)
class SubtipoGlosaAdmin(ImportExportModelAdmin):
    resource_class = SubtipoGlosaResource
    list_display = ('codigo', 'nombre', 'tipo_glosa')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo_glosa',)

@admin.register(SubCodigoGlosa)
class SubCodigoGlosaAdmin(ImportExportModelAdmin):
    resource_class = SubCodigoGlosaResource
    list_display = ('codigo', 'nombre', 'subtipo_glosa')
    search_fields = ('codigo', 'nombre')
    list_filter = ('subtipo_glosa',)

@admin.register(TipoGlosaRespuestaIPS)
class TipoGlosaRespuestaIPSAdmin(ImportExportModelAdmin):
    resource_class = TipoGlosaRespuestaIPSResource
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(SubtipoGlosaRespuestaIPS)
class SubtipoGlosaRespuestaIPSAdmin(ImportExportModelAdmin):
    resource_class = SubtipoGlosaRespuestaIPSResource
    list_display = ('codigo', 'nombre', 'tipo_glosa_respuesta')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo_glosa_respuesta',)

@admin.register(Glosa)
class GlosaAdmin(ImportExportModelAdmin):
    resource_class = GlosaResource
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
class HistorialGlosaAdmin(ImportExportModelAdmin):
    resource_class = HistorialGlosaResource
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