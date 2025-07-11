from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Profile, CatalogoCUPS, CatalogoCIE10, CatalogoCUMS, CatalogoMunicipio, CatalogoPais

# Resources para import/export
class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile
        import_id_fields = ('user',)
        fields = ('id', 'user', 'role', 'entidad_nombre', 'nit', 'direccion', 'representante_legal')

class CatalogoCUPSResource(resources.ModelResource):
    class Meta:
        model = CatalogoCUPS
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'descripcion')

class CatalogoCIE10Resource(resources.ModelResource):
    class Meta:
        model = CatalogoCIE10
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'descripcion')

class CatalogoCUMSResource(resources.ModelResource):
    class Meta:
        model = CatalogoCUMS
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'descripcion')

class CatalogoMunicipioResource(resources.ModelResource):
    class Meta:
        model = CatalogoMunicipio
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'nombre')

class CatalogoPaisResource(resources.ModelResource):
    class Meta:
        model = CatalogoPais
        import_id_fields = ('codigo',)
        fields = ('id', 'codigo', 'nombre')

# Admin classes con import/export
@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    resource_class = ProfileResource
    list_display = ('user', 'role', 'entidad_nombre', 'nit')
    list_filter = ('role',)
    search_fields = ('user__username', 'entidad_nombre', 'nit')

@admin.register(CatalogoCUPS)
class CatalogoCUPSAdmin(ImportExportModelAdmin):
    resource_class = CatalogoCUPSResource
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')

@admin.register(CatalogoCIE10)
class CatalogoCIE10Admin(ImportExportModelAdmin):
    resource_class = CatalogoCIE10Resource
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')

@admin.register(CatalogoCUMS)
class CatalogoCUMSAdmin(ImportExportModelAdmin):
    resource_class = CatalogoCUMSResource
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')

@admin.register(CatalogoMunicipio)
class CatalogoMunicipioAdmin(ImportExportModelAdmin):
    resource_class = CatalogoMunicipioResource
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(CatalogoPais)
class CatalogoPaisAdmin(ImportExportModelAdmin):
    resource_class = CatalogoPaisResource
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')