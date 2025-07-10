from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import error_403, landing_page, dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('facturacion/', include('facturacion.urls')),
    path('auditoria/', include('auditoria.urls')),
    path('cartera/', include('cartera.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('403/', error_403, name='403'),
    path('', landing_page, name='landing'),
    path('dashboard/', dashboard_view, name='dashboard'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'auditoria_cuentas.views.error_403'
