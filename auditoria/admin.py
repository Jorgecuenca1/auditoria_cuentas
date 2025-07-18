from django.contrib import admin
from .models import Glosa, TipoGlosa, SubtipoGlosa, SubCodigoGlosa, TipoGlosaRespuestaIPS, SubtipoGlosaRespuestaIPS, HistorialGlosa, Conciliacion
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Recursos para import-export
class TipoGlosaResource(resources.ModelResource):
    class Meta:
        model = TipoGlosa
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion')


class SubtipoGlosaResource(resources.ModelResource):
    class Meta:
        model = SubtipoGlosa
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion', 'tipo_glosa')


class SubCodigoGlosaResource(resources.ModelResource):
    class Meta:
        model = SubCodigoGlosa
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion', 'subtipo_glosa')


class TipoGlosaRespuestaIPSResource(resources.ModelResource):
    class Meta:
        model = TipoGlosaRespuestaIPS
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion')


class SubtipoGlosaRespuestaIPSResource(resources.ModelResource):
    class Meta:
        model = SubtipoGlosaRespuestaIPS
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion', 'tipo_glosa_respuesta')


class GlosaResource(resources.ModelResource):
    class Meta:
        model = Glosa
        import_id_fields = ('id',)
        export_order = ('id', 'factura', 'paciente', 'tipo_glosa', 'subtipo_glosa', 'subcodigo_glosa', 'valor_glosado', 'justificacion', 'estado', 'fecha_creacion')


class HistorialGlosaResource(resources.ModelResource):
    class Meta:
        model = HistorialGlosa
        import_id_fields = ('id',)
        export_order = ('id', 'glosa', 'usuario', 'accion', 'detalles', 'fecha_cambio')


class ConciliacionResource(resources.ModelResource):
    class Meta:
        model = Conciliacion
        import_id_fields = ('id',)
        export_order = ('id', 'glosa', 'estado', 'fecha_inicio', 'fecha_fin', 'iniciada_por')


# Admin classes con import-export
@admin.register(TipoGlosa)
class TipoGlosaAdmin(ImportExportModelAdmin):
    resource_class = TipoGlosaResource
    list_display = ('codigo','nombre')
    search_fields = ('codigo',)


@admin.register(SubtipoGlosa)
class SubtipoGlosaAdmin(ImportExportModelAdmin):
    resource_class = SubtipoGlosaResource
    list_display = ('codigo', 'tipo_glosa','nombre')
    list_filter = ('tipo_glosa',)
    search_fields = ('codigo', 'descripcion')


@admin.register(SubCodigoGlosa)
class SubCodigoGlosaAdmin(ImportExportModelAdmin):
    resource_class = SubCodigoGlosaResource
    list_display = ('codigo', 'subtipo_glosa','nombre')
    list_filter = ('subtipo_glosa__tipo_glosa', 'subtipo_glosa')
    search_fields = ('codigo', 'descripcion')


@admin.register(TipoGlosaRespuestaIPS)
class TipoGlosaRespuestaIPSAdmin(ImportExportModelAdmin):
    resource_class = TipoGlosaRespuestaIPSResource
    list_display = ('codigo','nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(SubtipoGlosaRespuestaIPS)
class SubtipoGlosaRespuestaIPSAdmin(ImportExportModelAdmin):
    resource_class = SubtipoGlosaRespuestaIPSResource
    list_display = ('codigo', 'tipo_glosa_respuesta','nombre')
    list_filter = ('tipo_glosa_respuesta',)
    search_fields = ('codigo', 'descripcion')


@admin.register(Glosa)
class GlosaAdmin(ImportExportModelAdmin):
    resource_class = GlosaResource
    list_display = ('id', 'factura', 'estado', 'valor_glosado', 'fecha_glosa')
    list_filter = ('estado', 'fecha_glosa', 'factura__ips')
    search_fields = ('factura__numero', 'descripcion')


@admin.register(HistorialGlosa)
class HistorialGlosaAdmin(ImportExportModelAdmin):
    resource_class = HistorialGlosaResource
    list_display = ('id', 'glosa', 'usuario', 'accion', 'fecha_cambio')
    list_filter = ('accion', 'fecha_cambio', 'usuario')


@admin.register(Conciliacion)
class ConciliacionAdmin(ImportExportModelAdmin):
    resource_class = ConciliacionResource
    list_display = ('id', 'glosa', 'estado', 'fecha_inicio', 'fecha_fin', 'iniciada_por')
    list_filter = ('estado', 'fecha_inicio', 'iniciada_por')
    search_fields = ('glosa__factura__numero', 'respuesta_definitiva_et')
    readonly_fields = ('fecha_inicio', 'fecha_fin')