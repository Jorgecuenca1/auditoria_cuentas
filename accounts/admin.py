from django.contrib import admin
from .models import Profile, CatalogoCUPS, CatalogoCIE10, CatalogoCUMS, CatalogoMunicipio, CatalogoPais

admin.site.register(Profile)
admin.site.register(CatalogoCUPS)
admin.site.register(CatalogoCIE10)
admin.site.register(CatalogoCUMS)
admin.site.register(CatalogoMunicipio)
admin.site.register(CatalogoPais)