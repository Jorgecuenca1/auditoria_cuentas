from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import error_403

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('facturacion/', include('facturacion.urls')),
    path('auditoria/', include('auditoria.urls')),
    path('cartera/', include('cartera.urls')),
    path('403/', error_403, name='403'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'auditoria_cuentas.views.error_403'
