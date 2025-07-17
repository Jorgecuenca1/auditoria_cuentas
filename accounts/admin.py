from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, CatalogoCUPS, CatalogoCIE10, CatalogoCUMS, CatalogoMunicipio, CatalogoPais
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Recursos para import-export
class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile
        import_id_fields = ('user',)
        export_order = ('user', 'role', 'entidad_nombre', 'nit', 'direccion', 'representante_legal')


class CatalogoCUPSResource(resources.ModelResource):
    class Meta:
        model = CatalogoCUPS
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion')


class CatalogoCIE10Resource(resources.ModelResource):
    class Meta:
        model = CatalogoCIE10
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion')


class CatalogoCUMSResource(resources.ModelResource):
    class Meta:
        model = CatalogoCUMS
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'descripcion')


class CatalogoMunicipioResource(resources.ModelResource):
    class Meta:
        model = CatalogoMunicipio
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'nombre')


class CatalogoPaisResource(resources.ModelResource):
    class Meta:
        model = CatalogoPais
        import_id_fields = ('codigo',)
        export_order = ('codigo', 'nombre')


# Inline para Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


# User Admin personalizado
class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('profile__role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__entidad_nombre')
    ordering = ('username',)

    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'Sin rol'
    get_role.short_description = 'Rol'


# Admin classes con import-export
@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    resource_class = ProfileResource
    list_display = ('user', 'role', 'entidad_nombre', 'nit')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'entidad_nombre', 'nit')
    ordering = ('role', 'entidad_nombre')


@admin.register(CatalogoCUPS)
class CatalogoCUPSAdmin(ImportExportModelAdmin):
    resource_class = CatalogoCUPSResource
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)


@admin.register(CatalogoCIE10)
class CatalogoCIE10Admin(ImportExportModelAdmin):
    resource_class = CatalogoCIE10Resource
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)


@admin.register(CatalogoCUMS)
class CatalogoCUMSAdmin(ImportExportModelAdmin):
    resource_class = CatalogoCUMSResource
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)


@admin.register(CatalogoMunicipio)
class CatalogoMunicipioAdmin(ImportExportModelAdmin):
    resource_class = CatalogoMunicipioResource
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)


@admin.register(CatalogoPais)
class CatalogoPaisAdmin(ImportExportModelAdmin):
    resource_class = CatalogoPaisResource
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')
    ordering = ('codigo',)


# Re-registrar User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)