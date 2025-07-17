from django.contrib import admin
from .models import Glosa, TipoGlosa, SubtipoGlosa, SubCodigoGlosa, TipoGlosaRespuestaIPS, SubtipoGlosaRespuestaIPS, HistorialGlosa
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


@admin.register(HistorialGlosa)
class HistorialGlosaAdmin(ImportExportModelAdmin):
    resource_class = HistorialGlosaResource
    list_display = ('id', 'glosa', 'usuario',)
    list_filter = ('accion', 'fecha_cambio', 'usuario')